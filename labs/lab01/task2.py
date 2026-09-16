import os
import sys

# Додаємо шлях до кореневої папки для імпорту shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    """Головна функція для виконання Завдання 2."""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60)

    # Вхідні дані для Варіанту 2
    users = {
        "sysadmin02": {
            "role": "system_admin",
            "clearance": 4,
            "department": "Infrastructure",
            "active": True,
        },
        "analyst234": {
            "role": "security_analyst",
            "clearance": 3,
            "department": "SOC",
            "active": True,
        },
        "developer567": {
            "role": "developer",
            "clearance": 2,
            "department": "Development",
            "active": True,
        },
        "intern890": {
            "role": "intern",
            "clearance": 1,
            "department": "HR",
            "active": True,
        },
        "external123": {
            "role": "external",
            "clearance": 1,
            "department": "Vendor",
            "active": False,
        },
    }

    resources = [
        ("prod_database", 4),
        ("dev_environment", 2),
        ("documentation", 1),
        ("source_code", 3),
        ("server_configs", 4),
        ("test_data", 2),
        ("compliance_docs", 3),
        ("system_logs", 4),
        ("project_files", 2),
        ("public_wiki", 1),
    ]

    security_levels = ("Open", "Internal", "Restricted", "Top Secret")
    blocked_users = {"external123", "old_account", "test_user"}

    # 1. Виведення списку ресурсів із текстовими рівнями безпеки
    print("СПИСОК РЕСУРСІВ:")
    for res_name, res_level in resources:
        # Індексація в кортежі починається з 0, тому віднімаємо 1
        text_level = security_levels[res_level - 1]
        print(f"- {res_name}: {text_level}")

    print("\n" + "=" * 60 + "\n")
    print("РЕЗУЛЬТАТИ ПЕРЕВІРКИ ДОСТУПУ:")

    # Додамо користувача 'unknown_user', щоб протестувати умову "User not found"
    users_to_test = list(users.keys()) + ["unknown_user"]

    # 2. Алгоритм перевірки доступу
    for username in users_to_test:
        for res_name, res_level in resources:
            # Перевірка 1: Користувача немає в системі
            if username not in users:
                print(
                    f"user={username:<15} resource={res_name:<18} -> DENY (User not found)"
                )
                continue

            # Перевірка 2: Користувач заблокований
            if username in blocked_users:
                print(
                    f"user={username:<15} resource={res_name:<18} -> DENY (User is blocked)"
                )
                continue

            user_data = users[username]

            # Перевірка 3: Акаунт неактивний
            if not user_data.get("active", False):
                print(
                    f"user={username:<15} resource={res_name:<18} -> DENY (Account inactive)"
                )
                continue

            # Перевірка 4 та 5: Порівняння рівнів допуску
            user_clearance = user_data.get("clearance", 0)
            if user_clearance >= res_level:
                print(f"user={username:<15} resource={res_name:<18} -> ALLOW")
            else:
                print(
                    f"user={username:<15} resource={res_name:<18} -> DENY (Insufficient clearance)"
                )

        print("-" * 60)


if __name__ == "__main__":
    main()
