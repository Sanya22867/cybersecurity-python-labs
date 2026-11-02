import json
import sqlite3
from contextlib import closing
from pathlib import Path
from labs.lab03.database import get_connection

BASE_DIR = Path(__file__).resolve().parent
SEED_FILE = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    """Читання JSON та початкове заповнення бази в одній транзакції."""
    if not SEED_FILE.exists():
        print(f"Помилка: файл {SEED_FILE} не знайдено.")
        return

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            print(
                "База вже містить дані. Повторне заповнення скасовано (без дублікатів)."
            )
            return

        try:
            with connection:
                for cat in categories:
                    connection.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"]),
                    )

                for rec in records:
                    connection.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        ),
                    )
            print("Початкові дані успішно додано до бази (3 категорії, 8 записів).")
        except sqlite3.IntegrityError as e:
            print(
                f"Помилка цілісності даних (наприклад, дублікат або неіснуюча категорія): {e}. Весь пакет змін скасовано."
            )
        except Exception as e:
            print(f"Неочікувана помилка: {e}. Усі зміни скасовано.")


if __name__ == "__main__":
    seed_database()
