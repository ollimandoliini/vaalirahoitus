#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import pprint
import json


base_url = 'https://www.vaalirahoitusvalvonta.fi'
frontpage = base_url + '/fi/index/vaalirahailmoituksia/ilmoituslistaus/EV2019.html'


def get_electoral_district_urls():
    html = requests.get(frontpage).content
    soup = BeautifulSoup(html, features='html.parser')

    electoral_district_urls = [base_url + i['href']
                               for i in soup.find(
        'div', {'class': 'center'}).find('p').findChildren('a')]
    return electoral_district_urls


def get_candidates_by_district(district_url):
    html = requests.get(district_url).content
    tags = BeautifulSoup(html, features="html.parser").findAll('tr')
    candidates = [row.find('td').text.replace(u'\xa0', u' ')
                  for row in tags if row.find('td')]
    return candidates


def candidates_and_urls(district_url):
    html = requests.get(district_url).content
    soup = BeautifulSoup(html, features='html.parser')
    print('---')
    candidates = []
    for row in soup.findAll('tr'):
        name = row.find('td')
        if name:
            candidate = {}
            candidate['Nimi'] = name.text.replace(u'\xa0', ' ')
            link = row.find('a')
            candidate['url'] = base_url + link['href'] if link else ''
            candidates.append(candidate)

    return candidates


def get_all_candidates():
    all_candidates = [candidates_and_urls(
        i) for i in get_electoral_district_urls()]
    flatten_list = [item for sublist in all_candidates for item in sublist]
    return flatten_list


def get_candidate_data(url):

    data = {}
    r = requests.get(url).content
    soup = BeautifulSoup(r, features='html.parser').find(
        'div', {'class': 'ann_form'})

    info_table = soup.find(lambda x: 'A.' in x.text.strip()
                           ).findNext('div').findAll('td')

    print('Fetching ' + info_table[0].text.strip())
    data['Arvo, ammatti tai toimi'] = info_table[1].text.strip()
    data['Puolue/valitsijayhdistys'] = info_table[2].text.strip()
    data['Vaalipiiri'] = info_table[3].text.strip()
    data['Tukiryhmä'] = info_table[5].text.strip()

    summary_table = soup.find(lambda x: 'B.' in x.text.strip()).findNext('div')

    for row in summary_table.findAll('tr'):
        th_tag = row.find('th')
        description = th_tag.text.strip()
        amount = th_tag.findNext('td').text.strip().replace(
            ' ', '').replace(',', '.')
        try:
            data[description] = float(amount) if len(amount) > 0 else 0
        except ValueError:
            print('Unknown value: ' + amount)
            data[description] = 0

    return data


if __name__ == "__main__":
    all_candidates = get_all_candidates()
    with_data = []

    for count, candidate in enumerate(all_candidates):
        print('Item', count)
        if candidate['url']:
            fetched_data = get_candidate_data(candidate['url'])
            candidate = {**candidate, **fetched_data}
            with_data.append(candidate)
        else:
            with_data.append(candidate)

    with open('data.json', 'w') as outputfile:
        json.dump(with_data, outputfile)
