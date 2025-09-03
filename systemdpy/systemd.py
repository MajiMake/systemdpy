import os
import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Dict

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SystemctlManager(ABC):
    _status_codes: Dict[str, Dict[int, str]] = {
        "status": {
            0: "Юнит {unit_name} активен или запущен",
            1: "Юнит {unit_name} неактивен, но существует PID файл (возможное состояние is-failed)",
            2: "Юнит {unit_name} неактивен, но существует lock файл (устаревшее/неиспользуемое состояние)",
            3: "Юнит {unit_name} неактивен или не запущен",
            4: "Статус юнита {unit_name} не может быть определен (юнит не существует)",
        },
        "start": {
            0: "Юнит {unit_name} успешно запущен",
            1: "Не удалось запустить юнит {unit_name}: Юнит уже активен или произошла ошибка",
        },
        "stop": {
            0: "Юнит {unit_name} успешно остановлен (теперь неактивен)",
            1: "Не удалось остановить юнит {unit_name}: Юнит уже неактивен или произошла ошибка",
        },
        "enable": {
            0: "Юнит {unit_name} успешно включен",
            1: "Не удалось включить юнит {unit_name}: Юнит не существует или произошла ошибка",
        },
        "disable": {
            0: "Юнит {unit_name} успешно отключен",
            1: "Не удалось отключить юнит {unit_name}: Юнит не существует или произошла ошибка",
        },
        "restart": {
            0: "Юнит {unit_name} успешно перезапущен",
            1: "Не удалось перезапустить юнит {unit_name}: Юнит не найден или произошла ошибка",
        },
        "reload": {
            0: "Юнит {unit_name} успешно перезагружен",
            1: "Не удалось перезагрузить юнит {unit_name}: Юнит не найден или произошла ошибка",
        },
        "mask": {
            0: "Юнит {unit_name} успешно замаскирован (не может быть запущен вручную или автоматически)",
            1: "Не удалось замаскировать юнит {unit_name}: Юнит не найден или произошла ошибка",
        },
        "unmask": {
            0: "Юнит {unit_name} успешно размаскирован (может быть запущен снова)",
            1: "Не удалось размаскировать юнит {unit_name}: Юнит не найден или произошла ошибка",
        },
        "daemon-reload": {
            0: "Демон успешно перезагружен (файлы юнитов перечитаны)",
            1: "Не удалось перезагрузить демон: недостаточно прав или системная ошибка",
}
    }
    def __init__(self, unit_name: str):
        self.config = None
        self.unit_name = unit_name
        self.unit_path = f"/etc/systemd/system/{unit_name}"

    def generate(self, config: BaseModel) -> str:
        self.config = config
        def iter_sections():
            for section_name in type(self.config).model_fields:
                section = getattr(self.config, section_name)
                if not section:
                    continue
                params = section.model_dump(exclude_none=True)
                yield section_name, params

        lines = []

        for section_name, params in iter_sections():
            if not params:
                continue
            lines.append(f"[{section_name}]")

            for key, value in params.items():
                if isinstance(value, list):
                    for item in value:
                        lines.append(f"{key}={item}")
                else:
                    lines.append(f"{key}={value}")

            lines.append("")

        return "\n".join(lines).strip()

    def create(self) -> bool:
        try:
            with open(self.unit_path, "w") as f:
                f.write(self.generate(self.config))
            os.chmod(self.unit_path, 0o644)
            logger.debug(f"{self.unit_type} {self.unit_name} успешно создан.")
            return True
        except PermissionError:
            logger.error("ошибка: требуются права root.")
            return False
        except Exception as e:
            logger.error(f"ошибка при создании {self.unit_type} {self.unit_name}: {e}")
            return False

    @property
    @abstractmethod
    def unit_type(self) -> str:
        pass

    def systemctl(self, action: str, *params: str) -> subprocess.CompletedProcess:
        cmd = ["systemctl", action, *params, "--quiet", self.unit_name]
        return subprocess.run(cmd)

    def daemon_reload(self) -> None:
        cmd = ["systemctl", "daemon-reload", "--quiet"]
        response = subprocess.run(cmd)
        status = self._status_codes["daemon-reload"].get(response.returncode, "Неизвестная ошибка")
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def enable(self, *params: str) -> None:
        response = self.systemctl("enable", *params)
        status = self._status_codes["enable"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def disable(self, *params: str) -> None:
        response = self.systemctl("disable", *params)
        status = self._status_codes["disable"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def start(self, *params: str) -> None:
        response = self.systemctl("start", *params)
        status = self._status_codes["start"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def restart(self, *params: str) -> None:
        response = self.systemctl("restart", *params)
        status = self._status_codes["restart"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def stop(self, *params: str) -> None:
        response = self.systemctl("stop", *params)
        status = self._status_codes["stop"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def status(self, *params: str) -> None:
        response = self.systemctl("status", *params)
        status = self._status_codes["status"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def reload(self, *params: str) -> None:
        response = self.systemctl("reload", *params)
        status = self._status_codes["reload"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def mask(self, *params: str) -> None:
        response = self.systemctl("mask", *params)
        status = self._status_codes["mask"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)

    def unmask(self, *params: str) -> None:
        response = self.systemctl("unmask", *params)
        status = self._status_codes["unmask"].get(response.returncode, "Неизвестная ошибка").format(unit_name=self.unit_name)
        logger.debug(status) if response.returncode == 0 else logger.warning(status)


class SystemdServiceManager(SystemctlManager):
    def __init__(self, service_name: str):
        super().__init__(service_name)

    @property
    def unit_type(self) -> str:
        return "service"


class SystemdTimerManager(SystemctlManager):
    def __init__(self, timer_name: str):
        super().__init__(timer_name)

    @property
    def unit_type(self) -> str:
        return "timer"
