import re
from typing import List, Dict, ClassVar

import requests
from bs4 import BeautifulSoup

from apps.data.models import TenderBase
from apps.parsing import selectors
from apps.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Tender(TenderBase):
    """Класс для парсинга данных о тендерах с сайта 'rostender.info'"""
    BASE_URL: ClassVar[str] = settings.BASE_URL

    def __init__(self,
                 tender_id: str,
                 title_and_url: tuple[str, str],
                 execution_place: str,
                 region_name: str,
                 starting_price: str,
                 publication_date: str,
                 deadline_msk: str,
                 categories: list[str]
                 ):

        super().__init__(
            tender_id=tender_id,
            title_and_url=title_and_url,
            execution_place=execution_place,
            region_name=region_name,
            starting_price=starting_price,
            publication_date=publication_date,
            deadline_msk=deadline_msk,
            categories=categories
        )

    def __repr__(self):
        return f'<Tender id={self.tender_id}>'

    @classmethod
    def from_url(cls, base_url: str) -> List['Tender']:
        """
        Загружает страницу и парсит все тендеры
        :param base_url: URL страницы со списком тендеров
        """
        logger.info(f'Загрузка страницы: {base_url}')
        try:
            response = requests.get(base_url, headers={'User-Agent': settings.USER_AGENT})
            response.raise_for_status()
            logger.info(f'Статус ответа: {response.status_code}')
        except requests.RequestException as e:
            logger.error(f'Ошибка при запросе к {base_url}: {e}')
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        # Забирает все блоки тендеров на странице
        tender_rows = soup.find_all(**selectors.TENDER_ROW_FIND_ARGS)

        if not tender_rows:
            logger.warning('На странице не найдено ни одного тендера.')
            return []

        logger.info(f'Найдено {len(tender_rows)} тендеров на странице.')

        tenders = []
        # Цикл по каждому тендру
        for i, row in enumerate(tender_rows, start=1):
            try:
                tender = cls._from_single_row(row)
                tenders.append(tender)
                logger.debug(f'Тендер {i} успешно распаршен: {tender}')
            except Exception as e:
                logger.error(f'Ошибка при парсинге тендера #{i}: {e}', exc_info=True)
                continue

        logger.info(f'Успешно распаршено {len(tenders)} тендеров из {len(tender_rows)}')
        return tenders

    @classmethod
    def _from_single_row(cls, row: BeautifulSoup) -> 'Tender':
        """
        Парсит один тендер
        :param row: HTML-элемент одного тендера
        """

        return cls(
            tender_id=cls._parser_tender_id(row),
            title_and_url=cls._parser_title_and_url(row),
            execution_place=cls._parser_execution_place(row),
            region_name=cls._parser_region_name(row),
            starting_price=cls._parser_starting_price(row),
            publication_date=cls._parser_publication_date(row),
            deadline_msk=cls._parser_deadline_msk(row),
            categories=cls._parser_categories(row)
        )

    @staticmethod
    def _parser_tender_id(soup: BeautifulSoup) -> str:
        """Парсит id тендера"""
        span = soup.select_one(selectors.TENDER_ID)
        if span:
            text = span.get_text(strip=True)
            match = re.search(r'№(\d+)', text)
            if match:
                return match.group(1) if match else ""
        return ""

    @staticmethod
    def _parser_title_and_url(soup: BeautifulSoup) -> tuple[str, str]:
        """Парсит название тендера и ссылку на детали"""
        link = soup.select_one(selectors.TITLE_AND_URL)
        if link:
            title = link.get_text(strip=True)
            tender_url = 'https://rostender.info/' + link['href']
            return title, tender_url
        return '-', '-'

    @staticmethod
    def _parser_execution_place(soup: BeautifulSoup) -> str:
        """Парсит место выполнения поставки"""
        execution_place = soup.select_one(selectors.EXECUTION_PLACE)
        if execution_place:
            return execution_place.get_text(strip=True)
        return '-'

    @staticmethod
    def _parser_region_name(soup: BeautifulSoup) -> str:
        """Парсит название региона"""
        region_name = soup.select_one(selectors.REGION_NAME)
        if region_name:
            return region_name.get_text(strip=True)
        return '-'

    @staticmethod
    def _parser_starting_price(soup: BeautifulSoup) -> str:
        """Парсит начальную цену"""
        starting_price = soup.select_one(selectors.STARTING_PRICE)
        if starting_price:
            text = starting_price.get_text(strip=True)
            if text != '—':
                match = re.search(r'\d+(?:\s+\d+)*', text.replace(' ', ''))
                if match:
                    return match.group(0)
        return '-'

    @staticmethod
    def _parser_publication_date(soup: BeautifulSoup) -> str:
        """Парсит дату открытия тендера"""
        publication_date = soup.select_one(selectors.PUBLICATION_DATE)
        if publication_date:
            text = publication_date.get_text(strip=True)
            match = re.search(r'\d{2}\.\d{2}\.\d{2}', text)
            if match:
                return match.group(0)
        return '-'

    @staticmethod
    def _parser_deadline_msk(soup: BeautifulSoup) -> str:
        """Парсит дату и время окончания приёма заявок (МСК)"""
        countdown = soup.select_one(selectors.DEADLINE_MSK)
        if not countdown:
            return '-'

        full_text = countdown.get_text(strip=True)
        # Извлечение даты
        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', full_text)
        # Извлечение времени
        time_match = re.search(r'\d{2}:\d{2}', full_text)

        date_str = date_match.group(0) if date_match else ''
        time_str = time_match.group(0) if time_match else ''

        if date_str and time_str:
            return f'{date_str} {time_str}'
        return date_str or time_str or '-'

    @staticmethod
    def _parser_categories(soup: BeautifulSoup) -> list[str]:
        """Парсит список отраслей, к которым относится тендер"""
        ul = soup.find(**selectors.CATEGORIES_LIST)
        if not ul:
            return []

        categories = ul.find_all(**selectors.CATEGORIES)
        return [res.get_text(strip=True) for res in categories if res]

    def to_dict(self) -> Dict[str, any]:
        """
        Преобразует объект Tender в словарь для экспорта в CSV
        :return: Словарь с данными тендера
        """
        title, url = self.title_and_url
        return {
            'tender_id': self.tender_id,
            'title': title,
            'url': url,
            'execution_place': self.execution_place,
            'region_name': self.region_name,
            'starting_price': self.starting_price,
            'publication_date': self.publication_date,
            'deadline_msk': self.deadline_msk,
            'categories': self.categories
        }
