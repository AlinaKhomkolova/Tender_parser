import argparse

from apps.data.saver import save_to_csv
from apps.utils.utils import get_tenders_parsing
from config.settings import settings


def main():
    parser = argparse.ArgumentParser(description='Парсер тендеров с rostender.info')
    parser.add_argument('--max', type=int, default=settings.COUNT_TENDERS,
                        help='Максимальное количество тендеров для парсинга (по умолчанию: 100)')
    parser.add_argument('--output', type=str, default=settings.OUTPUT_FILE,
                        help='Имя выходного файла (по умолчанию: tenders.csv)')

    args = parser.parse_args()
    all_tenders = get_tenders_parsing(args.max)

    # Сохранение в файл
    save_to_csv(all_tenders, args.output)


if __name__ == '__main__':
    main()
