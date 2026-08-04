from enum import StrEnum

class Capability(StrEnum):
    CONTAINERS = "containers"
    DOCKER = "docker"
    DOCKER_COMPOSE = "docker-compose"
    SYSTEM_PACKAGES = "system-packages"
    APT = "apt"
    SYSTEMD = "systemd"
    PERSISTENT_STORAGE = "persistent-storage"
    APP_PERSISTENT_STORAGE = "app-persistent-storage"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    SECRETS = "secrets"
    IDENTITY = "identity"
    APP_PROXY = "app-proxy"
    REVERSE_PROXY = "reverse-proxy"
    CONTAINER_NETWORK = "container-network"
    HOST_NETWORK = "host-network"
    HEALTHCHECK = "healthcheck"
    LOGGING = "logging"
    METRICS = "metrics"
    BACKUP = "backup"
    ROLLBACK = "rollback"
    FIREWALL = "firewall"
    HOST_DISK_MANAGEMENT = "host-disk-management"
    HOST_REBOOT = "host-reboot"

ALL_CAPABILITIES = tuple(item.value for item in Capability)
