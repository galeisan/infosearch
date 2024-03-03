import math
import os
import re
from collections import Counter

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Инициализация лемматизатора
morph = pymorphy2.MorphAnalyzer()

input_folder = "pages"  # Путь к папке с файлами выкачки
output_folder_for_tokens = "tokens_tf-idf"  # Путь к папке для сохранения результата токенов
output_folder_for_lemmas = "lemmas_tf-idf"  # Путь к папке для сохранения результата лемм
inverted_lemmas_file = "inverted_index.txt"
inverted_tokens_file = "inverted_tokens_index.txt"
total_documents = len(os.listdir(input_folder))


def create_inverted_index_tokens():
    index = {}

    for i in range(1, total_documents):
        with open(os.path.join(input_folder, f'{i}.html'), 'r', encoding='utf-8') as file:
            document = file.read()
            tokens = process_document(document)
            unique_tokens = list(set(tokens))

            for token in unique_tokens:
                if token in index:
                    index[token].append(i)
                else:
                    index[token] = [i]

    with open(inverted_tokens_file, 'w', encoding='utf-8') as output_file:
        for i in index:
            output_file.write(i + ": " + ", ".join(map(lambda file_number: str(file_number), index[i])) + "\n")


def inverted_index_count(file):
    token_pages = {}
    for line in file:
        token, pages = line.strip().split(': ')
        pages_list = [int(page) for page in pages.split(', ')]
        token_pages[token] = len(pages_list)
    return token_pages


def process_document(html_content):
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


def get_tokens_and_lemmas_count(tokens):
    token_counts = Counter(tokens)

    # Лемматизация токенов
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens]
    lemmatized_token_counts = Counter(lemmatized_tokens)

    return token_counts, lemmatized_token_counts


def calculate_tf(token_counts):
    total_tokens = sum(token_counts.values())
    tf = {token: count / total_tokens for token, count in token_counts.items()}
    return tf


# Функция для подсчета TF-IDF для каждого токена в каждом HTML-файле
def calculate_idf(token_counts, tokens_pages):
    # Подсчет TF-IDF для каждого токена в документе
    idf_data = {}
    for token, count in token_counts.items():
        if token in tokens_pages:
            idf_data[token] = math.log(total_documents / tokens_pages[token])
    return idf_data


def main():
    # создаем инвертированный индекс для токенов
    create_inverted_index_tokens()

    # по всем документам с помощью инвертированного индекса считаем кол-во появлений в документах
    with open(inverted_tokens_file, 'r', encoding='utf-8') as file:
        tokens_count_by_pages = inverted_index_count(file)

    with open(inverted_lemmas_file, 'r', encoding='utf-8') as file:
        lemmas_count_by_pages = inverted_index_count(file)

    if not os.path.exists(output_folder_for_tokens):
        os.makedirs(output_folder_for_tokens)

    if not os.path.exists(output_folder_for_lemmas):
        os.makedirs(output_folder_for_lemmas)

    # Обработка каждого файла выкачки
    for i in range(1, total_documents):
        with open(os.path.join(input_folder, f'{i}.html'), 'r', encoding='utf-8') as file:
            document = file.read()
            # получаем Counter для токенов и для лемм в текущем документе
            token_counts, lemmatized_token_counts = get_tokens_and_lemmas_count(process_document(document))

            # Подсчет TF, IDF для токенов
            tf_tokens = calculate_tf(token_counts)
            idf_tokens = calculate_idf(token_counts, tokens_count_by_pages)

            # Подсчет TF, IDF для лемм
            tf_lemma = calculate_tf(lemmatized_token_counts)
            idf_lemma = calculate_idf(lemmatized_token_counts, lemmas_count_by_pages)

            # Запись результатов в файл для токенов
            with open(os.path.join(output_folder_for_tokens, f"{i}_tokens.txt"), 'w', encoding='utf-8') as output_file:
                for token, res in tf_tokens.items():
                    output_file.write(f"{token} {idf_tokens[token]} {tf_tokens[token] * idf_tokens[token]}\n")

            # Запись результатов в файл для лемм
            with open(os.path.join(output_folder_for_lemmas, f"{i}_lemmas.txt"), 'w', encoding='utf-8') as output_file:
                for lemma, res in tf_lemma.items():
                    output_file.write(f"{lemma} {idf_lemma[lemma]} {tf_lemma[lemma] * idf_lemma[lemma]}\n")


if __name__ == "__main__":
    main()
