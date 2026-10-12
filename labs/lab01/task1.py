import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def evaluate_passwords(passwords_list, criteria_dict, forbidden_set):
    """Оцінює список паролів за заданими критеріями."""
    results = []
    min_len = criteria_dict["min_length"]

    pwd_counts = {}
    for p in passwords_list:
        pwd_counts[p] = pwd_counts.get(p, 0) + 1

    for pwd in passwords_list:
        is_forbidden = (
            pwd.lower() in [f.lower() for f in forbidden_set] or len(pwd) < min_len
        )
        if is_forbidden:
            results.append((pwd, "Заборонений"))
            continue

        has_digit = any(c.isdigit() for c in pwd)
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_special = any(not c.isalnum() for c in pwd)

        criteria_met = sum([has_digit, has_upper, has_lower, has_special])
        all_criteria = has_digit and has_upper and has_lower and has_special

        is_unique = pwd_counts[pwd] == 1
        is_long_enough = len(pwd) >= min_len + 4

        if all_criteria and is_long_enough and is_unique:
            status = "Дуже сильний"
        elif all_criteria and not is_long_enough:
            status = "Сильний"
        elif 1 < criteria_met < 4:
            status = "Середній"
        elif criteria_met >= 1:
            status = "Слабкий"
        else:
            status = "Невідомо"

        results.append((pwd, status))

    return results


def main():
    """Завдання 1"""
    print(f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}")
    print("=" * 60)

    passwords = [
        "Hello123!",
        "simple",
        "CompL3x@Pass",
        "password",
        "Strong#2023",
        "weak",
        "MySecur3!",
        "12345",
        "Advanced@1",
        "basic",
    ]
    criteria = {
        "min_length": 10,
        "require_digits": True,
        "require_upper": True,
        "require_special": True,
    }
    forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}

    for _ in range(3):
        random_index = random.randint(0, len(passwords) - 1)
        passwords.append(passwords[random_index])

    evaluated_passwords = evaluate_passwords(passwords, criteria, forbidden_passwords)

    print(f"{'Пароль':<20} | {'Надійність':<15}")
    print("-" * 40)
    for pwd, status in evaluated_passwords:
        print(f"{pwd:<20} | {status:<15}")


if __name__ == "__main__":
    main()
