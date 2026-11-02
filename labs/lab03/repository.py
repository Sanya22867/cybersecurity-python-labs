import sqlite3
from contextlib import closing
from typing import List, Dict, Any, Optional

from labs.lab03.database import get_connection


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Перетворює рядок результату SQLite на зручний словник."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_categories() -> List[Dict[str, Any]]:
    with closing(get_connection()) as connection:
        connection.row_factory = dict_factory
        return connection.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()


def create_category(name: str) -> Dict[str, Any]:
    with closing(get_connection()) as connection:
        connection.row_factory = dict_factory
        with connection:
            cursor = connection.execute(
                "INSERT INTO categories (name) VALUES (?)", (name,)
            )
            category_id = cursor.lastrowid
        return connection.execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        ).fetchone()


def delete_category(category_id: int) -> bool:
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM categories WHERE id = ?", (category_id,)
            )
            return cursor.rowcount > 0


def get_record(record_id: int) -> Optional[Dict[str, Any]]:
    query = """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name as category_name
            FROM records r
                     JOIN categories c ON r.category_id = c.id
            WHERE r.id = ? \
            """
    with closing(get_connection()) as connection:
        connection.row_factory = dict_factory
        return connection.execute(query, (record_id,)).fetchone()


def create_record(data: Dict[str, Any]) -> Dict[str, Any]:
    query = """
            INSERT INTO records (code, title, category_id, value, status)
            VALUES (?, ?, ?, ?, ?) \
            """
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                query,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                ),
            )
            record_id = cursor.lastrowid

    return get_record(record_id)


def get_records(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    min_value: Optional[float] = None,
    q: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    query = """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name as category_name
            FROM records r
                     JOIN categories c ON r.category_id = c.id
            WHERE 1 = 1 \
            """
    params = []

    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)
    if status is not None:
        query += " AND r.status = ?"
        params.append(status)
    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)
    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)

    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as connection:
        connection.row_factory = dict_factory
        return connection.execute(query, params).fetchall()


def update_record(record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    query = """
            UPDATE records
            SET code        = ?, \
                title       = ?, \
                category_id = ?, \
                value       = ?, \
                status      = ?
            WHERE id = ? \
            """
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                query,
                (
                    data["code"],
                    data["title"],
                    data["category_id"],
                    data["value"],
                    data["status"],
                    record_id,
                ),
            )
            if cursor.rowcount == 0:
                return None

    return get_record(record_id)


def delete_record(record_id: int) -> bool:
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM records WHERE id = ?", (record_id,)
            )
            return cursor.rowcount > 0


def bulk_create_records(records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Пакетне створення записів у межах однієї транзакції."""
    insert_query = """
                   INSERT INTO records (code, title, category_id, value, status)
                   VALUES (?, ?, ?, ?, ?) 
                   """
    inserted_ids = []

    with closing(get_connection()) as connection:
        with connection:
            for data in records_data:
                cursor = connection.execute(
                    insert_query,
                    (
                        data["code"],
                        data["title"],
                        data["category_id"],
                        data["value"],
                        data["status"],
                    ),
                )
                inserted_ids.append(cursor.lastrowid)

    return [get_record(rid) for rid in inserted_ids]
