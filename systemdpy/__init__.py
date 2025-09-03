"""
systemdpy - Пакет для создания и управления systemd сервисами и таймерами на Python.
"""

from .systemd import SystemdServiceManager, SystemdTimerManager
from .systemd_models import (
    UnitConfig,
    ServiceConfig,
    TimerConfig,
    InstallConfig,
    ServiceUnit,
    TimerUnit,
    UserType,
    RestartPolicy,
    LogOutput,
    TimeUnit
)

__version__ = "0.1.0"
__author__ = "Elson"
__email__ = "magomed.ibragimov@sofitlabs.com"

__all__ = [
    "SystemdServiceManager",
    "SystemdTimerManager",
    "UnitConfig",
    "ServiceConfig",
    "TimerConfig",
    "InstallConfig",
    "ServiceUnit",
    "TimerUnit",
    "UserType",
    "RestartPolicy",
    "LogOutput",
    "TimeUnit"
]
