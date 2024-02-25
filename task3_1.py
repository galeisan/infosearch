import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from bs4 import BeautifulSoup

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


# Извлечение токенов из HTML-страницы
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser').find('body')

    # удаляем ненужные теги
    for script in soup(["script", "style", "a", "span", "button", "label", "footer", "article"]):
        script.extract()

    # извлечение текста из HTML, удаляем все пробелы и переносы
    text = soup.get_text(separator=' ', strip=True)

    # токенизация текста
    tokens_page = word_tokenize(text)
    # приведение токенов к нижнему регистру, оставляем только слова
    tokens_page = [word.lower() for word in tokens_page if word.isalpha()]

    # оставляем только русские слова
    russian_pattern = re.compile('[а-яА-ЯёЁ]+')
    tokens_page = [word for word in tokens_page if russian_pattern.match(word)]

    # удаление стоп-слов
    stop_words = stopwords.words("russian")
    tokens_page = [word for word in tokens_page if word not in stop_words]

    return tokens_page


# Создание инвертированного списка
def create_inverted_index(lemmas_file):
    inverted_index = {}

    # Чтение списка лемм из файла
    with open(lemmas_file, 'r', encoding='utf-8') as f:
        terms_list = f.read().splitlines()

    # Прохождение по всем HTML-файлам
    for i in range(1, 148):
        html_file = f'pages/{i}.html'
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        text = extract_text_from_html(html_content)
        # Проверка каждого термина из списка в тексте
        for word in text:
            for term in terms_list:
                pattern = r'\b' + re.escape(word) + r'\b'
                match = re.search(pattern, term)
                lemma = term.split()[0]
                number = re.search(r'\d+', html_file).group()
                if match:
                    if lemma in inverted_index:
                        inverted_index[lemma].add(number)
                    else:
                        inverted_index[lemma] = {number}

    return inverted_index


lemmas_file = 'lemmas.txt'
inverted_index = create_inverted_index(lemmas_file)

# Запись инвертированного списка терминов
with open('inverted_index.txt', 'w', encoding='utf-8') as file:
    for key, value in inverted_index.items():
        # Преобразование значения из множества в строку
        value = sorted(value, key=int)
        value_str = ', '.join(str(v) for v in value)
        file.write(f"{key} {value_str}\n")
