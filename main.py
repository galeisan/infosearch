import requests
import bs4
import os

os.chdir("C://Users//user//PycharmProjects//infosearch//pages")

search = 'requests'
url = 'https://moreskazok.ru/tolstoj-a-n.html'
response = requests.get(url)

tree = bs4.BeautifulSoup(response.text, 'html.parser')

with open('index.txt', "w") as txtFile:
    k = 1
    for item in tree.select('td'):
        file_name = str(k) + '.html'
        page_url = f"https://moreskazok.ru/tolstoj-a-n.html{item.select_one('a').get('href')}"
        response2 = requests.get(page_url)
        line = file_name + ' ' + page_url + '\n'
        txtFile.write(line)
        with open(file_name, "wb") as htmlFile:
            htmlFile.write(response2.content)
            print(file_name)
        k += 1
