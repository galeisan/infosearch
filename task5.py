import math
import operator
import os
import numpy as np
import pandas as pd
import pymorphy2
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

morph = pymorphy2.MorphAnalyzer()
stop_words = stopwords.words("russian")

input_folder = '/Users/lyaysanz/Desktop/infosearch/lemmas_tf-idf'
n_docs = len(os.listdir(input_folder))
lemmas_file = '/Users/lyaysanz/Desktop/infosearch/lemmas.txt'
inverted_index_file = '/Users/lyaysanz/Desktop/infosearch/inverted_index.txt'
words_set = []

with open(lemmas_file, 'r', encoding='utf-8') as file:
    # Подсчитываем количество строк
    line_count = sum(1 for line in file)

n_words_set = line_count


# Создаем матрицу, где строки - номера файлов, столбцы - леммы, а значения ячеек это tf-idf
def create_vector_matrix():
    with open(lemmas_file, 'r', encoding='utf-8') as file:
        lemmas = file.read().splitlines()
        for lemma in lemmas:
            lemma = lemma.split(':')
            words_set.append(lemma[0])

    df_tf_idf = pd.DataFrame(np.zeros((n_docs + 1, n_words_set)), columns=words_set)

    for i in range(1, n_docs + 1):
        with open(os.path.join(input_folder, f'{i}_lemmas.txt'), 'r', encoding='utf-8') as file:
            document = file.read().splitlines()
            for line in document:
                line = line.split()
                w = line[0]
                tf_idf = round(float(line[2]), 8)
                df_tf_idf.loc[i, w] = tf_idf

    return df_tf_idf


df_tf_idf = create_vector_matrix()


# Считаем tf запроса
def calculate_tf(query):
    words = query.split()
    words = [word for word in words if word not in stop_words]
    # Подсчитываем количество вхождений каждого слова в предложении
    word_counts = {}
    for word in words:
        word = morph.parse(word)[0].normal_form
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1
    # Нормализуем количество вхождений каждого слова
    total_words = len(words)
    tf = {}
    for word, count in word_counts.items():
        tf[word] = count / total_words
    return tf


# Считаем idf запроса
def calculate_idf(token_counts, query):
    tokens = query.split()
    tokens = [token for token in tokens if token not in stop_words]
    lemmas = []
    for token in tokens:
        lemmas.append(morph.parse(token)[0].normal_form)
    idf_data = {}
    for token, count in token_counts.items():
        if token in lemmas:
            idf_data[token] = math.log(n_docs / token_counts[token])
    return idf_data


def inverted_index_count(file):
    token_pages = {}
    for line in file:
        token, pages = line.strip().split(': ')
        pages_list = [int(page) for page in pages.split(', ')]
        token_pages[token] = len(pages_list)
    return token_pages


with open(inverted_index_file, 'r', encoding='utf-8') as file:
    tokens_count_by_pages = inverted_index_count(file)


# Считаем tf-idf запроса
def calculate_tf_idf(tf, idf):
    tf_idf = {}
    for lemma, res in tf.items():
        tf_idf[lemma] = tf[lemma] * idf[lemma]
    return tf_idf


# Вычисляем косинусное сходство вектора запроса и векторов документов
def calculate_similarities(query):
    res = calculate_tf_idf(calculate_tf(query), calculate_idf(tokens_count_by_pages, query))
    # Преобразуем словарь в DataFrame
    vector_df = pd.DataFrame.from_dict(res, orient='index', columns=['вектор'])

    # Переиндексируем DataFrame
    vector_df = vector_df.reindex(df_tf_idf.columns, fill_value=0.0)

    # Вычисляем косинусное сходство
    cos_sim = cosine_similarity(vector_df.values.reshape(1, -1), df_tf_idf.values)

    similarity_dict = {}

    # Предположим, что у вас есть список номеров файлов
    file_numbers = df_tf_idf.index.tolist()

    # Перебираем номера файлов и соответствующие им значения косинусного сходства
    for file_number, similarity_value in zip(file_numbers, cos_sim[0]):
        similarity_dict[file_number] = similarity_value
    return dict(sorted(similarity_dict.items(), key=operator.itemgetter(1), reverse=True))


# Вводим запрос
while True:
    query = input("Введите запрос: ")
    if query.lower() == 'exit':
        exit()
    try:
        print(calculate_similarities(query))
        result = calculate_similarities(query)
        dict_items = result.items()
        with open('pages/index.txt', 'r') as file:
            links = file.read().splitlines()
            for key, value in dict_items:
                if value > 0:
                    print(links[int(key) - 1])
    except Exception as e:
        print(f"Error occurred: {e}. Please try again")

