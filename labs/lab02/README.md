## Детальний посібник із запуску та роботи (Гайд)

Усі команди запускаються з кореневої директорії репозиторію `cybersecurity-python-labs`. Програма взаємодіє через інтерфейс командного рядка (CLI) та використовує модуль `argparse` для обробки аргументів.


### Активація віртуального середовища (у корені проєкту):
    .venv\Scripts\Activate.ps1

### Завдання 1 (Демонстрація ООП)
    python -m labs.lab02.main demo

### Завдання 2 (Режим генерації нового еталону):
    python -m labs.lab02.main analyze --dir labs/lab02/data/data_v02/monitored --baseline labs/lab02/data/data_v02/baseline_new.json --mode generate

### Завдання 2 (Режим перевірки на зміни):
    python -m labs.lab02.main analyze --dir labs/lab02/data/data_v02/monitored --baseline labs/lab02/data/data_v02/baseline.json --mode check

### Фінальна перевірка коду лінтером:
    ruff check
    ruff format