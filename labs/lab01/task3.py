import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


class ValidationError(Exception):
    """Власний виняток для валідації паролів."""


def check_min_length(password: str):
    """Перевірка мінімальної довжини пароля."""
    if len(password) < 10:
        raise ValidationError("Пароль занадто короткий (менше 10 символів).")
    """Власний виняток для валідації паролів."""


def log_event(func):
    """Декоратор для логування спроб автентифікації у JSON-файл."""

    def wrapper(username, password, *args, **kwargs):
        result = func(username, password, *args, **kwargs)
        event_data = {
            "event": "login",
            "user": username,
            "result": "success" if result else "failure",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "args": list(args),
            "kwargs": kwargs,
        }

        log_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "log.json")

        try:
            logs = []
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []

            logs.append(event_data)

            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)

        except (
            PermissionError,
            OSError,
        ) as e:
            print(f"[Помилка логування]: {e}")

        return result

    return wrapper


def generate_hash(password: str, salt: str = "00002") -> str:
    """Генерує шістнадцетковий хеш від конкатенації пароля та солі (sha3_224)."""
    if password is None or salt is None or password == "" or salt == "":
        raise ValueError("Пароль та сіль не можуть бути порожніми.")

    if len(password) < 10:
        raise ValidationError("Пароль занадто короткий (менше 10 символів).")

    raw_data = (password + salt).encode("utf-8")
    hash_obj = hashlib.sha3_224(raw_data)
    return hash_obj.hexdigest()


def create_user(username: str, password: str) -> tuple:
    """Створює пару (логін, хеш) з використанням персональної солі '00002'."""
    hash_value = generate_hash(password, salt="00002")
    return username, hash_value


def create_users(users_list: list):
    """Створює базу даних та записує її у CSV-файл."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "users.csv")

    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for uname, pwd in users_list:
                user_tuple = create_user(uname, pwd)
                writer.writerow(user_tuple)
    except (
        FileNotFoundError,
        PermissionError,
        OSError,
        ValidationError,
        ValueError,
    ) as e:
        print(f"[Помилка створення бази]: {e}")


def read_users_db() -> list:
    """Зчитує вміст CSV-файлу у список users_db."""
    csv_path = os.path.join(os.path.dirname(__file__), "data", "users.csv")
    users_db = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    users_db.append(row)
    except (
        FileNotFoundError,
        PermissionError,
        OSError,
    ) as e:
        print(f"[Помилка читання бази]: {e}")
    return users_db


@log_event
def login(username: str, password: str) -> bool:
    """Перевіряє автентифікацію користувача за базою даних."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми.")

    users_db = read_users_db()
    input_hash = generate_hash(password, salt="00002")

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == input_hash:
            return True

    return False


def main():
    """Головна функція для виконання Завдання 3."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60)

    try:
        users_to_register = (
            ("admin_sys", "CompL3x@Pass1"),
            ("analyst_23", "Strong#2023_a"),
            ("dev_alex", "Advanced@1_dev"),
            ("hr_anna", "MySecur3!_hr99"),
            ("user_test1", "Password123!"),
            ("user_test2", "SecureKey#99"),
            ("user_test3", "CipherPass@1"),
            ("user_test4", "Access_2023!"),
            ("user_test5", "Protected#01"),
            ("user_test6", "ElitePass@10"),
        )

        print("Створення бази даних користувачів...")
        create_users(users_to_register)

        db_content = read_users_db()
        print(f"\n{'Логін користувача':<20} | {'Хеш пароля (SHA3-224 + сіль)':<40}")
        print("-" * 65)
        for uname, uhash in db_content:
            print(f"{uname:<20} | {uhash:<40}")

        print("\n" + "=" * 60)
        print("ТЕСТУВАННЯ АВТЕНТИФІКАЦІЇ ТА ЛОГУВАННЯ:")

        res1 = login("dev_alex", "Advanced@1_dev")
        print(f"Вхід ('dev_alex'): {'Успішно' if res1 else 'Помилка'}")

        res2 = login("dev_alex", "wrong_pass")
        print(
            f"Вхід ('dev_alex' з невірним паролем): {'Успішно' if res2 else 'Помилка (очікувано)'}"
        )

        try:
            login("dev_alex", "short")
        except ValidationError as e:
            print(f"Перехоплено виняток валідації: {e}")

        try:
            login("", "")
        except ValueError as e:
            print(f"Перехоплено виняток значень: {e}")

        print("\nЛоги подій успішно записані у файл labs/lab01/data/log.json")

    except (
        ValidationError,
        ValueError,
    ) as err:
        print(f"[Критична помилка виконання]: {err}")


if __name__ == "__main__":
    main()
