from typing import List

from fastapi import FastAPI

from apps.utils.utils import get_tenders_parsing
from config.settings import settings

app = FastAPI(title="Tender Parser API", description="API для получения данных о тендерах")


@app.get("/tenders", response_model=List[dict])
def get_tenders():
    """
    Возвращает список тендеров в формате JSON.
    """
    count_tenders = settings.COUNT_TENDERS
    all_tenders = get_tenders_parsing(count_tenders)

    # Преобразование в словари
    return [t.to_dict() for t in all_tenders]
