import task1
import task2
import task3


def main():
    while True:
        print("\n" + "=" * 40)
        print("ГОЛОВНЕ МЕНЮ - ЛАБОРАТОРНА РОБОТА 1")
        print("1. Запустити Завдання 1 (Надійність паролів)")
        print("2. Запустити Завдання 2 (Контроль доступу)")
        print("3. Запустити Завдання 3 (Автентифікація та логування)")
        print("0. Вихід з програми")
        print("=" * 40)

        choice = input("Оберіть завдання для запуску (0-3): ")
        print("\n")

        if choice == "1":
            task1.main()
        elif choice == "2":
            task2.main()
        elif choice == "3":
            task3.main()
        elif choice == "0":
            print("Роботу завершено.")
            break
        else:
            print("Невірний вибір! Будь ласка, введіть число від 0 до 3.")


if __name__ == "__main__":
    main()
