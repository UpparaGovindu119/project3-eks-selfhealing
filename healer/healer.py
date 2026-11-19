import os
import time
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] healer: %(message)s",
)
logger = logging.getLogger("pod-healer")

NAMESPACE = os.getenv("WATCH_NAMESPACE", "production-app")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "15"))
MAX_RESTARTS_THRESHOLD = int(os.getenv("MAX_RESTARTS_THRESHOLD", "5"))


def load_k8s_config():
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes configuration.")
    except config.ConfigException:
        config.load_kube_config()
        logger.info("Loaded local kubeconfig.")


def evaluate_and_heal(v1: client.CoreV1Api, namespace: str):
    pods = v1.list_namespaced_pod(namespace=namespace).items
    for pod in pods:
        pod_name = pod.metadata.name
        # Skip the healer pod itself if running in same namespace
        if pod.metadata.labels and pod.metadata.labels.get("app") == "pod-healer":
            continue

        phase = pod.status.phase
        container_statuses = pod.status.container_statuses or []

        for cs in container_statuses:
            restarts = cs.restart_count or 0
            waiting_reason = cs.state.waiting.reason if cs.state and cs.state.waiting else None

            unhealthy_waiting = waiting_reason in {"CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"}
            excessive_restarts = restarts >= MAX_RESTARTS_THRESHOLD
            failed_phase = phase in {"Failed", "Unknown"}

            if unhealthy_waiting or excessive_restarts or failed_phase:
                logger.warning(
                    f"Detected unhealthy pod='{pod_name}' phase='{phase}' "
                    f"waiting='{waiting_reason}' restarts={restarts}. Triggering self-heal delete..."
                )
                try:
                    v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
                    logger.info(f"Self-healed: deleted pod='{pod_name}' in namespace='{namespace}' for controller recreation.")
                except ApiException as exc:
                    logger.error(f"Failed to delete pod='{pod_name}': {exc.reason}")


def main():
    load_k8s_config()
    v1 = client.CoreV1Api()
    logger.info(f"Starting Kubernetes Self-Healer on namespace='{NAMESPACE}' every {CHECK_INTERVAL}s...")

    while True:
        try:
            evaluate_and_heal(v1, NAMESPACE)
        except ApiException as exc:
            logger.error(f"Kubernetes API error: {exc.status} - {exc.reason}")
        except Exception as exc:
            logger.error(f"Unexpected error in healer loop: {exc}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
