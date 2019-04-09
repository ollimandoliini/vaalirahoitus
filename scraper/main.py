from bs4 import BeautifulSoup
import requests
import pprint

printer = pprint.PrettyPrinter()

base_url = 'https://www.vaalirahoitusvalvonta.fi'
frontpage = base_url + '/fi/index/vaalirahailmoituksia/ilmoituslistaus/EV2019.html'


def get_electoral_district_urls():
    r = requests.get(frontpage).content
    soup = BeautifulSoup(r, features='html.parser')

    electoral_district_urls = [base_url + i['href']
                               for i in soup.find(
        'div', {'class': 'center'}).find('p').findChildren('a')]
    return electoral_district_urls


def get_candidate_urls():
    district_pages = get_electoral_district_urls()
    candidate_urls = []
    for page in district_pages:
        r = requests.get(page).content
        soup = BeautifulSoup(r, features='html.parser')

        links = [base_url + tag['href'] for tag in soup.find_all(
            'a') if tag.text.strip() == 'Ennakkoilmoitus']
        candidate_urls.append(links)
    return sum(candidate_urls, [])


url = 'https://www.vaalirahoitusvalvonta.fi/fi/index/vaalirahailmoituksia/ilmoituslistaus/EV2019/03/jH5PvZth9/E_EI_EV2019.html'


def get_candidate_data(url):
    data = {}
    r = requests.get(url).content
    soup = BeautifulSoup(r, features='html.parser').find(
        'div', {'class': 'ann_form'})

    info_table = soup.find(lambda x: 'A.' in x.text.strip()
                           ).findNext('div').findAll('td')

    general_info = {}
    general_info['name'] = info_table[0].text.strip()
    general_info['profession'] = info_table[1].text.strip()
    general_info['party'] = info_table[2].text.strip()
    general_info['district'] = info_table[3].text.strip()
    general_info['support group'] = info_table[5].text.strip()
    data['general_info'] = general_info

    summary_table = soup.find(lambda x: 'B.' in x.text.strip()).findNext('div')
    funding_summary = {}

    data['funding summary'] = funding_summary

    for row in summary_table.findAll('tr'):
        th = row.find('th')
        amount = th.findNext('td').text.strip().replace(
            ' ', '').replace(',', '.')

        funding_summary[th.text.strip()] = float(
            amount) if len(amount) > 0 else 0

    return data


printer.pprint(get_candidate_data(url)['funding summary'])
