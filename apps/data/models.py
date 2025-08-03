from pydantic import BaseModel


class TenderBase(BaseModel):
    """
    :param tender_id: Уникальный идентификатор тендера
    :param title_and_url: Название тендера и ссылка на подробности
    :param execution_place: Место поставки
    :param region_name: Регион
    :param starting_price: Начальная цена (очищенная от пробелов и символов)
    :param publication_date: Дата открытия тендера (ДД.ММ.ГГ)
    :param deadline_msk: Дата и время окончания приёма заявок (МСК)
    :param categories: Список отраслей, к которым относится тендер
    """
    tender_id: str
    title_and_url: tuple[str, str]
    execution_place: str
    region_name: str
    starting_price: str
    publication_date: str
    deadline_msk: str
    categories: list[str]
