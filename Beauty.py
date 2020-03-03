import random
import requests
from bs4 import BeautifulSoup

class Beauty:
    def __init__(self, page):
        self.page = page
    def random_get_beautiful_lady(self):
        url = 'https://www.ptt.cc/bbs/Beauty/index.html'
        if self.page > 0:
            for i in range(self.page):
                res = requests.get(url, cookies={'over18': '1'})
                soup = BeautifulSoup(res.text, 'html.parser')
                tagName = 'div.title a'
                result = soup.select(tagName)
                nextPage = soup.find("div", {"class": "btn-group btn-group-paging"})
                nextPage = nextPage.find_all('a')
                url = 'https://www.ptt.cc' + nextPage[1].attrs["href"]

        res = requests.get(url, cookies={'over18': '1'})
        soup = BeautifulSoup(res.text, 'html.parser')
        tagName = 'div.title a'
        result = soup.select(tagName)
        if self.page == 0:
            ran = random.randint(0, len(result) - 6)
            print(result[ran].text, result[ran]['href'])
            title = result[ran].text
            sex_url = result[ran]['href']
        else:
            ran = random.randint(0, len(result) - 1)
            # print(result[ran].text, result[ran]['href'])
            title = result[ran].text
            sex_url = result[ran]['href']
        sex_url = 'https://www.ptt.cc' + sex_url
        res = requests.get(sex_url, cookies={'over18': '1'})
        soup = BeautifulSoup(res.text, 'html.parser')
        pic = soup.find('a', {'target': '_blank'})
        img = pic.text
        return title, sex_url, img