from enum import Enum
import re
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


class UnitConfig(BaseModel):
    """
    Модель для секции [Unit] в systemd.
    Используется как в сервисах (*.service), так и в таймерах (*.timer).
    """
    Description: Optional[str] = Field(
        default="",
        description="Описание юнита, отображаемое в systemctl status"
    )
    Documentation: Optional[List[str]] = Field(
        default=[],
        description="Ссылки на документацию (man:, http:, info: и т.д.)"
    )
    After: Optional[List[str]] = Field(
        default=[],
        description="Список юнитов, которые должны быть запущены перед этим"
    )
    Before: Optional[List[str]] = Field(
        default=[],
        description="Список юнитов, которые должны быть запущены после этого"
    )
    Requires: Optional[List[str]] = Field(
        default=[],
        description="Жёсткие зависимости - если эти юниты не запустятся, этот тоже не запустится"
    )
    Wants: Optional[List[str]] = Field(
        default=[],
        description="Мягкие зависимости - этот юнит попытается запуститься даже если зависимости не доступны"
    )
    Conflicts: Optional[List[str]] = Field(
        default=[],
        description="Юниты, которые не могут работать одновременно с этим"
    )
    ConditionPathExists: Optional[List[str]] = Field(
        default=[],
        description="Условие: файл или директория должны существовать"
    )

class InstallConfig(BaseModel):
    """
    Модель для секции [Install] в systemd.
    """
    WantedBy: Optional[List[str]] = Field(
        default=["multi-user.target"],
        description="Targets, в которые будет включён этот юнит при активации"
    )
    RequiredBy: Optional[List[str]] = Field(
        default=[],
        description="Targets, которые требуют этот юнит для своей работы"
    )
    Alias: Optional[List[str]] = Field(
        default=[],
        description="Дополнительные имена для этого юнита"
    )
    Also: Optional[List[str]] = Field(
        default=[],
        description="Дополнительные юниты, которые нужно активировать/деактивировать вместе с этим"
    )


class UserType(str, Enum):
    ROOT = "root"
    USER = "user"

    def __str__(self):
        return self.value

class RestartPolicy(str, Enum):
    NO = "no"
    ON_SUCCESS = "on-success"
    ON_FAILURE = "on-failure"
    ON_ABNORMAL = "on-abnormal"
    ON_WATCHDOG = "on-watchdog"
    ON_ABORT = "on-abort"
    ALWAYS = "always"

    def __str__(self):
        return self.value

class LogOutput(str, Enum):
    INHERIT = "inherit"
    JOURNAL = "journal"
    SYSLOG = "syslog"
    KMSG = "kmsg"
    FILE = "file"
    NULL = "null"

    def __str__(self):
        return self.value

class ServiceConfig(BaseModel):
    """
    Модель для секции [Service] в systemd unit-файлах.
    Охватывает основные параметры управления сервисом.
    """
    ExecStart: str = Field(
        ...,
        min_length=1,
        description="Команда или путь к исполняемому файлу для запуска сервиса"
    )
    ExecStartPre: Optional[List[str]] = Field(
        default=None,
        description="Команды, выполняемые перед основным процессом"
    )
    ExecStartPost: Optional[List[str]] = Field(
        default=None,
        description="Команды, выполняемые после успешного запуска основного процесса"
    )
    ExecStop: Optional[str] = Field(
        default=None,
        description="Команда для корректного завершения сервиса"
    )
    ExecStopPost: Optional[List[str]] = Field(
        default=None,
        description="Команды, выполняемые после остановки сервиса"
    )
    ExecReload: Optional[str] = Field(
        default=None,
        description="Команда для перезагрузки конфигурации сервиса"
    )
    WorkingDirectory: Optional[str] = Field(
        default=None,
        description="Рабочая директория сервиса"
    )
    User: UserType = Field(
        default=UserType.ROOT,
        description="Пользователь, от которого запускается сервис"
    )
    Group: Optional[str] = Field(
        default=None,
        description="Группа, от которой запускается сервис"
    )
    Restart: RestartPolicy = Field(
        default=RestartPolicy.NO,
        description="Политика перезапуска сервиса при различных условиях"
    )
    RestartSec: Optional[Union[int, float]] = Field(
        default=None,
        ge=0,
        description="Время ожидания перед перезапуском (в секундах)"
    )
    StandardOutput: LogOutput = Field(
        default=LogOutput.INHERIT,
        description="Куда перенаправлять stdout"
    )
    StandardError: LogOutput = Field(
        default=LogOutput.INHERIT,
        description="Куда перенаправлять stderr"
    )
    Environment: Optional[List[str]] = Field(
        default=None,
        description="Переменные окружения в формате VAR=value"
    )
    EnvironmentFile: Optional[List[str]] = Field(
        default=None,
        description="Файлы с переменными окружения (обычно .conf или .env)"
    )
    TimeoutStartSec: Optional[Union[int, float]] = Field(
        default=None,
        ge=0,
        description="Таймаут запуска сервиса (в секундах)"
    )
    TimeoutStopSec: Optional[Union[int, float]] = Field(
        default=None,
        ge=0,
        description="Таймаут остановки сервиса (в секундах)"
    )
    Type: Optional[Literal["simple", "forking", "oneshot", "dbus", "notify", "idle"]] = Field(
        default=None,
        description="Тип сервиса (поведение systemd)"
    )
    KillMode: Optional[Literal["control-group", "process", "mixed", "none"]] = Field(
        default=None,
        description="Как systemd должен завершать процессы сервиса"
    )

    # Валидаторы
    @field_validator('Environment', mode='before')
    def validate_environment(cls, v):
        if '=' not in v:
            raise ValueError('Переменные окружения должны быть в формате VAR=value')
        return v

    @field_validator('ExecStart')
    def validate_exec_start(cls, v):
        if v.strip() == "":
            raise ValueError('ExecStart не может быть пустым')
        return v

    class ConfigDict:
        use_enum_values = True
        extra = "forbid"


class TimeUnit(str, Enum):
    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    DAYS = "d"
    WEEKS = "w"
    MONTHS = "M"
    YEARS = "y"

    def __str__(self):
        return self.value

class TimerConfig(BaseModel):
    """
    Модель для секции [Timer] в systemd unit-файлах.
    Охватывает все основные параметры управления таймерами.
    """
    OnCalendar: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Календарное расписание в формате systemd.time(7) (например, '*-*-* 00:00:00')"
    )
    OnActiveSec: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Запуск через указанное время после активации таймера"
    )
    OnBootSec: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Запуск через указанное время после загрузки системы"
    )
    OnStartupSec: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Запуск через указанное время после первого запуска systemd"
    )
    OnUnitActiveSec: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Запуск через указанное время после последней активации юнита"
    )
    OnUnitInactiveSec: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Запуск через указанное время после последней деактивации юнита"
    )
    Unit: Optional[str] = Field(
        default=None,
        description="Имя юнита для активации (если отличается от имени таймера)"
    )
    Persistent: Optional[bool] = Field(
        default=None,
        description="Выполнять пропущенные срабатывания после простоя"
    )
    WakeSystem: Optional[bool] = Field(
        default=None,
        description="Пробуждать систему из спящего режима для срабатывания"
    )
    RemainAfterElapse: Optional[bool] = Field(
        default=None,
        description="Оставлять таймер активным после срабатывания"
    )
    AccuracySec: Optional[str] = Field(
        default="1min",
        description="Точность срабатывания (например, '1s', '5min')"
    )
    RandomizedDelaySec: Optional[str] = Field(
        default=None,
        description="Случайная задержка для распределения нагрузки"
    )
    FixedRandomDelay: Optional[bool] = Field(
        default=None,
        description="Фиксировать случайную задержку между перезапусками"
    )

    # Валидаторы
    @field_validator('OnCalendar')
    def validate_on_calendar(cls, v):
        # Приводим одиночную строку к списку
        values = v if isinstance(v, list) else [v]

        pattern = re.compile(
            r'^(@(yearly|annually|monthly|weekly|daily|hourly|reboot)|'
            r'(\d{4}|\*)-(\d{2}|\*)-(\d{2}|\*)'
            r'( (\d{2}|\*):(\d{2}|\*):(\d{2}|\*))?$|'
            r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)( \d{2}:\d{2}:\d{2})?)$'
        )

        for value in values:
            if not isinstance(value, str):
                raise ValueError(f'Записи OnCalendar должны быть строками, получено {type(value).__name__}')
            if not pattern.match(value.strip()):
                raise ValueError(
                    f'Неверный формат OnCalendar: "{value}". '
                    f'Проверьте systemd.time(7) для получения допустимых форматов.'
                )

        return v

    @field_validator('OnActiveSec', 'OnBootSec', 'OnStartupSec', 'OnUnitActiveSec', 'OnUnitInactiveSec', 
               'AccuracySec', 'RandomizedDelaySec', mode='before')
    def validate_time_spec(cls, v):
        if v and not re.match(r'^(\d+(\.\d+)?[smhdwMy]?|\d+:\d+:\d+)(\s+\d+(\.\d+)?[smhdwMy]?)*$', v):
            raise ValueError('Неверная спецификация времени. Используйте форматы типа "5s", "1.5h", "2d 12h"')
        return v

    @field_validator('Unit')
    def validate_unit(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9@_\-\.]+\.(service|socket|target|path)$', v):
            raise ValueError('Имя юнита должно заканчиваться допустимым типом юнита (например, .service)')
        return v

    class ConfigDict:
        extra = "forbid"
        json_encoders = {
            TimeUnit: lambda v: v.value,
        }

class ServiceUnit(BaseModel):
    Unit: UnitConfig
    Service: ServiceConfig
    Install: InstallConfig


class TimerUnit(BaseModel):
    Unit: UnitConfig
    Timer: TimerConfig
    Install: InstallConfig
