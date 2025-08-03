import csv
from typing import List

from apps.parsing.parser import Tender
from apps.utils.logger import get_logger

logger = get_logger(__name__)


def save_to_csv(tenders: List[Tender], filename: str):
    """
    Сохраняет список тендеров в csv-файл
    :param tenders: Список объектов Tender
    :param filename: Имя файла
    """
    if not tenders:
        logger.warning("Нет данных для сохранения: список тендеров пуст.")
        return

    # Данные в виде словарей
    data = [t.to_dict() for t in tenders]
    # Определение заголовков (ключевые поля)
    fieldnames = data[0].keys()

    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()  # Записывает заголовки
            writer.writerows(data)  # Записывает строки

        logger.info(f"Данные успешно сохранены в файл: {filename} (записано {len(tenders)} строк)")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в {filename}: {e}", exc_info=True)
        raise
