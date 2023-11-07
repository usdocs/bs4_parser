import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from collections import defaultdict
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, EXPECTED_STATUS, PEP_ZERO_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', class_='sphinxsidebarwrapper')
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is None:
            version, status = a_tag.text, ''
        else:
            version, status = text_match.groups()
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )

    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    if response is None:
        return
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    # status_count = {}
    status_count = defaultdict(int)
    response = get_response(session, PEP_ZERO_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    main_section = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'}
    )
    pep_table = find_tag(
        main_section,
        'table',
        attrs={'class': 'pep-zero-table'}
    )
    tbody_in_table = find_tag(pep_table, 'tbody')
    tr_in_tbody = tbody_in_table.find_all('tr')

    logging_status = ['Несовпадающие статусы:']
    for tr in tqdm(tr_in_tbody):
        first_column_tag = find_tag(tr, 'td')
        preview_status = first_column_tag.text[1:]

        version_a_tag = find_tag(tr, 'a')
        href = version_a_tag['href']
        version_link = urljoin(PEP_ZERO_URL, href)

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        main_section = find_tag(
            soup, 'section', attrs={'id': 'pep-content'}
        )
        field_list_in_section = find_tag(
            main_section, 'dl', attrs={'class': 'rfc2822'}
        )
        status_line = field_list_in_section.find_next(
            string='Status'
        ).parent
        status = status_line.next_sibling.next_sibling.text
        # status_count[status] = status_count.get(status, 0) + 1
        status_count[status] += 1
        if status not in EXPECTED_STATUS[preview_status]:
            logging_status.append(
                (f'{version_link}\n'
                 f'Статус в карточке: {status}\n'
                 f'Ожидаемые статусы:'
                 f'{EXPECTED_STATUS[preview_status]}')
            )

    if len(logging_status) > 1:
        logging.info('\n'.join(logging_status))

    results = [('Статус', 'Количество')]
    results.extend(status_count.items())
    results.append(
        ('Total:', sum(status_count.values()))
    )
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
