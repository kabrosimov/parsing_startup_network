from bs4 import BeautifulSoup
import requests
import json
import re
import os
import time


def get_data(url, page_num):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    req = requests.get(f"{url}{page_num}/", headers=headers)
    src = req.text
    if not os.path.isdir(f"lesson3/data/page_{i}"):
        os.mkdir(f"lesson3/data/page_{i}")
    with open(f"lesson3/data/page_{i}/page.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open(f"lesson3/data/page_{i}/page.html", "r", encoding="utf-8") as file:
        src = file.read()
    return src


def get_link_in_page(page_text):
    soup = BeautifulSoup(page_text, 'lxml')
    find_tag = soup.find_all(class_='projects_list_b')
    link_dict = {}
    print(len(find_tag))
    for item_num, item in enumerate(find_tag):

        link_href = item['href']
        link_title = item.find(class_='title').text
        # print(link_title)
        if link_title == '':
            link_title = f"unknown_title_{item_num}"
        rep = [' ', ',', '-', "'", ':', '"', '/', '.', '<', '>', '|']
        for elem in rep:
            if elem in link_title:
                link_title = link_title.replace(elem, '_')
        link_dict[link_title] = link_href

    return link_dict


def get_data_startup(dict_of_links):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    count_links = int(len(dict_of_links)) - 1
    json_list = []
    for k, v in dict_of_links.items():
        req = requests.get(v, headers=headers)
        src = req.text

        with open(f"lesson3/data/page_{i}/{k}.html", "w", encoding="utf-8") as file:
            file.write(src)

        with open(f"lesson3/data/page_{i}/{k}.html", "r", encoding="utf-8") as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        # print(v)
        startup_info = soup.find(class_='main_b')
        startup_code = startup_info.find(class_='code').text
        try:
            startup_img = soup.find(
                'div', id='big_photo_view').find('img')['src']
        except Exception:
            startup_img = 'No images'
        # print(startup_img)
        startup_name = soup.find('div', class_='main_b_c').find('h1').text
        startup_header = startup_info.find(class_='main_d').find_all('span')
        startup_industry_tag = soup.find(string=re.compile('Отрасль'))
        if startup_industry_tag is None:
            startup_industry_tag = soup.find(string=re.compile('Market'))
        startup_industry_tag_span = startup_industry_tag.find_next()
        # print(startup_industry_tag_span)
        startup_industry = startup_industry_tag_span.text
        startup_countries = startup_industry_tag_span.find_previous(
            'span').text
        next_spans = startup_industry_tag_span.find_all_next('span')
        startup_study = next_spans[0].text
        startup_last_update = next_spans[1].text
        try:
            startup_idea = soup.find('div', id='IDEA').find(
                'span', itemprop='description').text
        except Exception:
            startup_idea = 'No idea text'
        team_list = []
        try:
            startup_teams = soup.find('div', id='FOLK').find_all('a')
            for startup_team in startup_teams:

                startup_team_href = startup_team['href']
                startup_team_head_name = startup_team.find(
                    'div', class_='name').text
                startup_team_head_role = startup_team.find(
                    'div', class_='role').text
                team_list.append({
                    "startup_team_href": startup_team_href,
                    "startup_team_head_name": startup_team_head_name,
                    "startup_team_head_role": startup_team_head_role,
                })

        except Exception:
            team_list = []

        json_list.append(
            {
                "startup_url": v,
                "startup_code": startup_code,
                "startup_name": startup_name,
                "startup_countries": startup_countries,
                "startup_study": startup_study,
                "startup_last_update": startup_last_update,
                "startup_img": startup_img,
                "startup_idea": startup_idea,
                "startup_team": team_list,


            }
        )
        print(f"Осталось:{count_links}")

        count_links -= 1
    # print(i)
    with open(f"lesson3/data/page_{i}/data.json", "w", encoding="utf-8") as file:
        json.dump(json_list, file, indent=4, ensure_ascii=False)

    # return json_list

    # print(link_title, link_href)


print(time.asctime())
count_startup = 0
for i in range(1, 16):
    print(f"Станица {i}")
    src = get_data("https://by.startup.network/startups/page/", i)
    link_dict = get_link_in_page(src)
    count_startup += int(len(link_dict))
    get_data_startup(link_dict)

print(time.asctime())
print(f"Записано: {count_startup} стартапов")

# write summary json file
json_list = []
for i in range(1, 16):
    with open(f"lesson3/data/page_{i}/data.json", "r", encoding="utf-8") as file:
        # src = file.read()
        st = json.load(file)
        json_list.extend(st)
with open("lesson3/data/summary_data.json", "w", encoding="utf-8") as file:
    json.dump(json_list, file, indent=4, ensure_ascii=False)

# print(link_dict.values())
