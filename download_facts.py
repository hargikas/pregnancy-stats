import json
import io
import re

import requests
from bs4 import BeautifulSoup


def donwload(url):
    with requests.get(url) as response:
        return response.text


def has_info(href):
    return href and re.compile("/pregnancy/week-by-week/week").search(href)


def parse_html(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    data = []
    week = []
    for item in soup.find_all(href=has_info):
        if item.string:
            week[0] = item.string
        for img in item.find_all("img"):
            if img.get('src'):
                if week:
                    data.append(week)
                week = [None, None, None]
                url = 'http:' + img.get('src')
                week[2] = url
        for desc in item.find_next_siblings("div"):
            if desc.string:
                week[1] = desc.string
    data.append(week)

    # Fix week 1 and 2
    full_data = [data[0][:]] + data
    full_data[0][0] = 'Week 1 of Pregnancy'
    full_data[1][0] = 'Week 2 of Pregnancy'

    # Make it tuples
    clean_data = [tuple(i) for i in full_data]

    return clean_data


def save(data):
    with io.open('pregnancy.facts', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    html_doc = donwload('https://www.whattoexpect.com/pregnancy/week-by-week/')
    data = parse_html(html_doc)
    save(data)
