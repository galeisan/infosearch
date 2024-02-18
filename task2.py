# coding=utf-8
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pymorphy2
import re
from bs4 import BeautifulSoup
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# список для хранения токенов со всех страниц
tokens = list()


# функция для извлечения токенов из HTML-страницы
def get_tokens_from_page(page):
    with open(page, 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
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


# функция для группировки токенов по леммам
def group_tokens_by_lemmas(unique_tokens):

    # инициализация объекта pymorphy2 для лемматизации
    morph = pymorphy2.MorphAnalyzer()
    grouped_tokens = {}

    for token in unique_tokens:
        # лемматизация каждого токена
        parsed_token = morph.parse(token)[0]
        lemma = parsed_token.normal_form

        # группировка токенов по леммам
        if lemma not in grouped_tokens:
            grouped_tokens[lemma] = []
        grouped_tokens[lemma].append(token)

    return grouped_tokens


# обработка каждой страницы и извлечение токенов
for i in range(1, 148):
    page_tokens = get_tokens_from_page(f'pages/{i}.html')
    tokens.extend(page_tokens)

# получение уникальных токенов
unique_tokens = list(set(tokens))
# группировка токенов по леммам
grouped_tokens = group_tokens_by_lemmas(unique_tokens)

# запись уникальных токенов в файл
with open('tokens.txt', 'w', encoding='utf-8') as file:
    for token in unique_tokens:
        file.write(token + '\n')

# запись групп токенов по леммам в файл
with open('lemmas.txt', 'w', encoding='utf-8') as file:
    for key, values in grouped_tokens.items():
        values_str = ' '.join(values)
        file.write(f"{key}: {values_str}\n")
