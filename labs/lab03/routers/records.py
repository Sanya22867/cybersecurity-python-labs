import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=List[RecordRead])
def get_records(
    category_id: Optional[int] = Query(None, ge=1, description="Лише записи категорії"),
    status: Optional[str] = Query(None, description="Лише записи з цим статусом"),
    min_value: Optional[float] = Query(None, ge=0, description="value >= min_value"),
    q: Optional[str] = Query(
        None, min_length=1, max_length=120, description="Буквальний підрядок у title"
    ),
    limit: int = Query(20, ge=1, le=100, description="Максимальна кількість записів"),
    offset: int = Query(0, ge=0, description="Кількість пропущених записів"),
):
    """Отримати список записів із підтримкою фільтрації та пагінації."""
    return repository.get_records(category_id, status, min_value, q, limit, offset)


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int):
    """Отримати один запис за його id."""
    record = repository.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    return record


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(record: RecordCreate):
    """Створити новий запис."""
    try:
        return repository.create_record(record.model_dump())
    except sqlite3.IntegrityError as e:
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg or "records.category_id" in error_msg:
            raise HTTPException(status_code=404, detail="Вказана категорія не існує")
        if "unique constraint" in error_msg or "records.code" in error_msg:
            raise HTTPException(status_code=409, detail="Запис із таким code вже існує")
        raise HTTPException(status_code=422, detail="Порушення обмежень даних")


@router.put("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, record: RecordReplace):
    """Повністю замінити змінювані поля наявного запису."""
    try:
        updated_record = repository.update_record(record_id, record.model_dump())
        if not updated_record:
            raise HTTPException(status_code=404, detail="Запис не знайдено")
        return updated_record
    except sqlite3.IntegrityError as e:
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg or "records.category_id" in error_msg:
            raise HTTPException(status_code=404, detail="Вказана категорія не існує")
        if "unique constraint" in error_msg or "records.code" in error_msg:
            raise HTTPException(status_code=409, detail="Запис із таким code вже існує")
        raise HTTPException(status_code=422, detail="Порушення обмежень даних")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int):
    """Видалити запис."""
    deleted = repository.delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Запис не знайдено")


@router.post(
    "/bulk", response_model=List[RecordRead], status_code=status.HTTP_201_CREATED
)
def bulk_create_records(records: List[RecordCreate]):
    """Пакетне створення записів з атомарним збереженням."""
    if not (1 <= len(records) <= 100):
        raise HTTPException(
            status_code=422, detail="Пакет має містити від 1 до 100 елементів"
        )

    codes = [r.code for r in records]
    if len(codes) != len(set(codes)):
        raise HTTPException(status_code=409, detail="Пакет містить дублікати code")

    try:
        return repository.bulk_create_records([r.model_dump() for r in records])
    except sqlite3.IntegrityError as e:
        error_msg = str(e).lower()
        if "foreign key constraint" in error_msg or "records.category_id" in error_msg:
            raise HTTPException(
                status_code=404, detail="Одна з вказаних категорій не існує"
            )
        if "unique constraint" in error_msg or "records.code" in error_msg:
            raise HTTPException(
                status_code=409,
                detail="Один із записів має code, який вже існує в базі",
            )
        raise HTTPException(status_code=422, detail="Порушення обмежень даних у пакеті")
