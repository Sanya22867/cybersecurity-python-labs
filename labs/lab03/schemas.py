from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=40)


class CategoryRead(CategoryCreate):
    id: int = Field(gt=0)


class RecordCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(min_length=3, max_length=40)
    title: str = Field(min_length=3, max_length=120)
    category_id: int = Field(gt=0)
    # Для Варіанта 2: float, від 0 до 10
    value: float = Field(ge=0, le=10, allow_inf_nan=False)
    status: Literal["new", "in_progress", "done"]


class RecordReplace(RecordCreate):
    """Модель для PUT-запиту. Усі змінювані поля обов'язкові, тому просто успадковуємо RecordCreate."""

    pass


class RecordRead(RecordCreate):
    """Модель для читання запису, яка містить id та назву категорії."""

    id: int = Field(gt=0)
    category_name: str
