import pandas as pd
from bs4 import BeautifulSoup

from urllib import request

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import os



def get_result_page_source(keyword, page_number):
    driver.get(URL.format(keyword=keyword, page_number=str(page_number)))
    # WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'hs-cnn-image')))
    time.sleep(10)
    return driver.page_source

def get_all_news_links(soup):
    links = []
    for div in soup.find_all("div", {"class": "hs-cn-new asd"}):
        links.append('http://' + div.find("a").get("href")[2:])
    return links[:5]

def get_article_from_soup(soup):
    try:
        return soup.find("div",{"class":"rhd-all-article-detail"}).get_text()
    except:
        return soup.find("div",{"class":"news-detail-text"}).get_text()

def get_title_from_soup(soup):
    return soup.title.get_text()

class New():
    def __init__(self, title, content, link):
        self.title = title
        self.content = content
        self.link = link


if __name__ == "__main__":

    KEYWORDS = ["finans"]
    MAX_PAGE_NUMBER = 2
    URL = 'http://www.hurriyet.com.tr/arama/#/?page={page_number}&key={keyword}&where=/&how=Article,Column,NewsPhotoGallery,NewsVideo&platform=/&isDetail=false'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('../driver/chromedriver.exe', options=chrome_options)

    news = []
    for keyword in KEYWORDS:
        for page_number in range(1, MAX_PAGE_NUMBER + 1):
            print("Page:{page_number} is opening...".format(page_number=page_number))
            page_source = get_result_page_source(keyword=keyword, page_number=page_number)
            search_page_soup = BeautifulSoup(page_source)
            news_links = get_all_news_links(soup=search_page_soup)

            for link in news_links:
                if 'video' not in link:
                    try:
                        driver.get(link)
                        time.sleep(2)
                        news_soup = BeautifulSoup(driver.page_source)
                        news_title = get_title_from_soup(soup=news_soup)
                        news_text = get_article_from_soup(soup=news_soup)
                        try:
                            news_text = news_text.split("SON 24 SAATTE YAŞANANLAR")[0]
                        except:
                            continue
                        new = New(news_title, news_text, link)

                        news.append(new)
                    except:
                        print('Failed link: {}'.format(link))
                        continue

    os.makedirs('../output', exist_ok=True)
    timestamp = time.time().__str__().split('.')[0]

    with open('../output/news-{}-{}-{}.csv'.format('-'.join(KEYWORDS), str(MAX_PAGE_NUMBER), timestamp),
              'w', encoding="utf-8") as f:
        f.write("ix|title|link|content\n")
        for ix, new in enumerate(news):
            f.write("{ix}|{new_title}|{new_link}|{new_content}\n".format(ix=ix,
                                                                         new_title=new.title,
                                                                         new_link=new.link,
                                                                         new_content=new.content))

    # sample read
    # df = pd.read_csv('../output/news-finans-2-1538656202.csv', sep='|')
