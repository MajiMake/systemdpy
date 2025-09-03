# systemdpy

Пакет для создания и управления systemd сервисами и таймерами на Python.

## Описание

systemdpy предоставляет удобный интерфейс для создания и управления systemd unit-файлами (сервисами и таймерами) с использованием Pydantic моделей для валидации конфигураций.

## Установка

```bash
pip install systemdpy
```

Или с помощью Poetry:

```bash
poetry add systemdpy
```

## Использование

### Создание сервиса

```python
from systemdpy import SystemdServiceManager
from systemdpy.models import ServiceUnit, UnitConfig, ServiceConfig, InstallConfig, UserType, RestartPolicy, StandardOutput

# Создание конфигурации сервиса
service_config = ServiceUnit(
    Unit=UnitConfig(
        Description="Мой тестовый сервис"
    ),
    Service=ServiceConfig(
        ExecStart="/usr/bin/python3 /path/to/script.py",
        User=UserType.ROOT,
        Restart=RestartPolicy.NO,
        StandardOutput=LogOutput.INHERIT
    ),
    Install=InstallConfig()
)

# Создание менеджера сервиса
manager = SystemdServiceManager("my-service.service")
manager.config = service_config

# Создание unit-файла
manager.create()

# Управление сервисом
manager.enable()
manager.start()
```

### Создание таймера

```python
from systemdpy import SystemdTimerManager
from systemdpy.models import TimerUnit, UnitConfig, TimerConfig, InstallConfig

# Создание конфигурации таймера
timer_config = TimerUnit(
    Unit=UnitConfig(
        Description="Таймер для ежедневного выполнения"
    ),
    Timer=TimerConfig(
        OnCalendar="*-*-* 00:00:00",  # Каждый день в полночь
        Unit="my-service.service"
    ),
    Install=InstallConfig()
)

# Создание менеджера таймера
manager = SystemdTimerManager("my-timer.timer")
manager.config = timer_config

# Создание unit-файла
manager.create()

# Управление таймером
manager.enable()
manager.start()
```

## API

### Классы

- `SystemdServiceManager` - Менеджер для управления сервисами
- `SystemdTimerManager` - Менеджер для управления таймерами

### Методы

- `create()` - Создание unit-файла
- `enable()` - Включение юнита
- `disable()` - Отключение юнита
- `start()` - Запуск юнита
- `stop()` - Остановка юнита
- `restart()` - Перезапуск юнита
- `status()` - Проверка статуса юнита
- `reload()` - Перезагрузка юнита
- `daemon_reload()` - Перезагрузка демона systemd

## Требования

- Python 3.12+
- systemd
- pydantic 2.11.7+

## Лицензия

MIT License

## Автор

Elson (magomed.ibragimov@sofitlabs.com)
