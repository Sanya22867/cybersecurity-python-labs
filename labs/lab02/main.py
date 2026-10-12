import argparse
from labs.lab02.task1 import User, Admin, UserAccount, AuditLog
from labs.lab02.task2 import run_fim


def demo_task1():
    print("=== Демонстрація Завдання 1 (ООП) ===")

    try:
        user1 = User("obekesha", "oleksandr_bekesha@lpnu.ua")
        user1.set_password("SecurePass123!")
        print(f"[+] Створено користувача: {user1}")
    except ValueError as e:
        print(f"Помилка: {e}")
        return

    try:
        user1.email = "bad-email"
    except ValueError as e:
        print(f"[-] Очікувана помилка валідації: {e}")

    admin = Admin("root", "admin@system.local")
    admin.set_password("RootPass1!")
    admin.grant_permission("READ_LOGS")
    admin.grant_permission("DELETE_USERS")
    print(f"[+] Створено адміністратора: {admin}")

    audit = AuditLog()
    account = UserAccount(user1, audit)

    print("\n--- Спроба входу ---")
    account.login("obekesha", "WrongPass!", "192.168.1.100")  # Невдалий
    account.login("obekesha", "SecurePass123!", "192.168.1.100")  # Успішний

    print(
        f"Статус аутентифікації: {'Увійшов' if account.is_authenticated() else 'Не увійшов'}"
    )

    account.logout()
    print(
        f"Статус після виходу: {'Увійшов' if account.is_authenticated() else 'Не увійшов'}"
    )

    print("\n--- Журнал Аудиту ---")
    account["audit_log"].show_all()


def main():
    parser = argparse.ArgumentParser(description="Лабораторна робота №2 - Кібербезпека")
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")

    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1 (ООП)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Запустити утиліту FIM (Завдання 2)"
    )
    analyze_parser.add_argument(
        "--dir", required=True, help="Директорія для моніторингу"
    )
    analyze_parser.add_argument(
        "--baseline", required=True, help="Шлях до файлу baseline.json"
    )
    analyze_parser.add_argument(
        "--mode",
        choices=["generate", "check"],
        required=True,
        help="Режим: generate або check",
    )
    analyze_parser.add_argument("--log-file", help="Файл для логування (опціонально)")

    args = parser.parse_args()

    if args.command == "demo":
        demo_task1()
    elif args.command == "analyze":
        run_fim(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
