import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def print_resources(resources, security_levels):
    """Виводить список ресурсів."""
    print("СПИСОК РЕСУРСІВ:")
    for res_name, res_level in resources:
        text_level = security_levels[res_level - 1]
        print(f"- {res_name}: {text_level}")


def check_access(username, res_name, res_level, users, blocked_users):
    """Перевіряє доступ для конкретного користувача та ресурсу."""
    if username not in users:
        print(f"user={username:<15} resource={res_name:<18} -> DENY (User not found)")
        return

    if username in blocked_users:
        print(f"user={username:<15} resource={res_name:<18} -> DENY (User is blocked)")
        return

    user_data = users[username]

    if not user_data.get("active", False):
        print(f"user={username:<15} resource={res_name:<18} -> DENY (Account inactive)")
        return

    user_clearance = user_data.get("clearance", 0)
    if user_clearance >= res_level:
        print(f"user={username:<15} resource={res_name:<18} -> ALLOW")
    else:
        print(
            f"user={username:<15} resource={res_name:<18} -> DENY (Insufficient clearance)"
        )


def main():
    """Завдання 2"""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60)

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

    print_resources(resources, security_levels)

    print("\n" + "=" * 60 + "\n")
    print("РЕЗУЛЬТАТИ ПЕРЕВІРКИ ДОСТУПУ:")

    users_to_test = list(users.keys()) + ["unknown_user"]

    for username in users_to_test:
        for res_name, res_level in resources:
            check_access(username, res_name, res_level, users, blocked_users)
        print("-" * 60)


if __name__ == "__main__":
    main()
