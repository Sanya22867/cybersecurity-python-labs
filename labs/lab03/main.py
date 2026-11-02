from contextlib import asynccontextmanager
from fastapi import FastAPI

from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared.student import STUDENT_NAME, GROUP_NAME, VARIANT_NUMBER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ініціалізація бази даних під час запуску застосунку (без перезапису даних)."""
    initialize_database()
    yield


app = FastAPI(
    title="Реєстр вразливостей мережевих сервісів",
    description="Сервіс обліку результатів навчальної перевірки мережевих сервісів. Одиниця вимірювання: score (оцінка небезпеки), поріг: 6.0.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["Health"])
def ping():
    """Перевірка доступності API."""
    return {"status": "ok"}


@app.get("/student", tags=["Student"])
def get_student_info():
    """Отримання даних студента."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }
