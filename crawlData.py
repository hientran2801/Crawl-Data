import requests
import pymongo
import re
from bs4 import BeautifulSoup

myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['colearn_textbook1']
colAnswers = mydb["answers"]
colCategories = mydb["categories"]

urlBase = "https://vietjack.com/"

def crawlInEx(url, parent):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    question = soup.find('b', attrs={"style": "color:green;"})
    name = question.text + '\n' + question.next_sibling.text
    print(name)

    answer = soup.findAll('p', attrs={"style": "text-align:justify;"})
    content = ''
    for i in answer:
        content += i.text + '\n'
    print(content)
    print(parent['_id'])
    colCategories.insert_one({'parent_id': parent['_id'], 'name': name, 'has_sub_category': 0})
    category_id = colCategories.find_one({'name': name})
    colAnswers.insert_one({'category_id': category_id['_id'], 'content': content})

def crawlInUnit(url, parent):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    execises = soup.find('ul', class_='list').find_all('li')
    for execise in execises:
        crawlInEx(urlBase + execise.find('a').get('href')[2:], parent)


def crawlInSubject(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    chapters = soup.findAll('div', class_="col-md-6")
    subject = soup.find('h1', class_='title')
    print(subject.text)
    colCategories.insert_one({'name': subject.text, 'has_sub_category': 1})
    subject = colCategories.find_one({'name': subject.text})
    for chapter in chapters:
        chapterName = chapter.find('h3', class_='sub-title')
        if chapterName != None:
            print("-------------------------")
            print(chapterName.text)
            colCategories.insert_one({'parent_id': subject['_id'] ,'name': chapterName.text, 'has_sub_category': 1})
            units = chapter.find_all('li')
            for unit in units:
                chapter = colCategories.find_one({'name': chapterName.text})
                print(unit.text)
                colCategories.insert_one({'parent_id': chapter['_id'], 'name': unit.text, 'has_sub_category': 1})

                parent = colCategories.find_one({'name': unit.text})
                # print(urlBase + unit.find('a').get('href')[2:])
                crawlInUnit(urlBase + unit.find('a').get('href')[2:], parent)


crawlInSubject("https://vietjack.com/cong-nghe-6-kn/index.jsp")
# crawlInUnit("https://vietjack.com//lich-su-6-ket-noi/bai-16-cac-cuoc-khoi-nghia-tieu-bieu-gianh-doc-lap-truoc-the-ki-x.jsp", '111')
# crawlInEx("https://vietjack.com//lich-su-6-ket-noi/cau-hoi-mo-dau-trang-70-bai-16-lich-su-lop-6-ket-noi-tri-thuc.jsp", '111')


