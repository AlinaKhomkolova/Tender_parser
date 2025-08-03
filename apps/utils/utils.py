from apps.parsing.parser import Tender
from apps.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


def get_tenders_parsing(count_tenders):
    page = 1
    all_tenders = []

    logger.info(f'Начало парсинга: требуется {count_tenders} тендеров')

    while len(all_tenders) < count_tenders:
        url = f'{settings.BASE_URL}?page={page}'
        logger.info(f'Парсинг страницы {page}: {url}')
        try:
            page_tenders = Tender.from_url(url)
            if not page_tenders:
                logger.warning('Сайт вернул пустую страницу. Больше нет тендеров.')
                break

            logger.debug(f'Найдено {len(page_tenders)} тендеров на странице {page}')
            all_tenders.extend(page_tenders)

            # Проверка, не превысили ли нужное количество
            if len(all_tenders) >= count_tenders:
                logger.info(f'Требуемое количество тендеров ({count_tenders}) достигнуто.')
                break

            page += 1

            # Защита от бесконечного цикла
            if page > 50:
                logger.warning('Достигнут лимит в 50 страниц. Остановка парсинга.')
                break

        except Exception as e:
            logger.error(f'Критическая ошибка при парсинге {url}: {e}', exc_info=True)
            break

    # Обрезает до нужного кол-ва
    all_tenders = all_tenders[:count_tenders]
    logger.info(f'Парсинг завершён. Успешно собрано {len(all_tenders)} тендеров.')

    return all_tenders
