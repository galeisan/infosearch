import re
import pymorphy2


# Чтение файла с инвертированным списком
def read_data_from_file(filename):
    inverted_index = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            lemma, file_number = line.strip().split(':')
            file_number = file_number.strip().split(', ')
            inverted_index[lemma] = set(file_number)

    return inverted_index


# Вычисление выражения со скобками
def evaluate_expression(expression, inverted_index):
    morph = pymorphy2.MorphAnalyzer()
    stack = []  # Стек для множеств
    operator_stack = []  # Стек для операторов
    tokens = re.findall(r'\(|\)|\w+|[^\s\w]', expression)
    tokens = list(filter(None, tokens))  # Разделение строки на элементы

    for token in tokens:
        if token in ["AND", "OR", "NOT", "(", ")"]:
            if token == "(":
                operator_stack.append(token)
            elif token == ")":
                while operator_stack and operator_stack[-1] != "(":
                    apply_operator(operator_stack.pop(), stack, inverted_index)
                operator_stack.pop()  # Удаляем открывающую скобки из стека операторов
            else:
                operator = token
                # Если токен - оператор, добавляем его в стек операторов
                # Если оператор уже был добавлен в стек, и приоритет текущего оператора меньше или равен приоритету оператора на вершине стека,
                # применяем оператор на вершине стека к двум верхним операндам из стека операндов.
                # Далее добавляем текущий оператор в стек операторов.
                if operator_stack and precedence(operator) <= precedence(operator_stack[-1]):
                    apply_operator(operator_stack.pop(), stack, inverted_index)
                operator_stack.append(token)
        else:
            token = morph.parse(token)[0].normal_form
            # Если токен - слово, добавляем соответствующее множество слов в стек множеств
            if token in inverted_index:
                stack.append(inverted_index[token])
            else:
                # Если такого слова не найдено в стеке, записываем его под несуществующим значением
                stack.append({'0'})

    while operator_stack:
        apply_operator(operator_stack.pop(), stack, inverted_index)

    return sorted(stack[-1], key=int)


def apply_operator(operator, stack, inverted_index):
    # Функция для применения операторов
    if operator == "AND":
        operand2 = stack.pop()
        operand1 = stack.pop()
        stack.append(operand1.intersection(operand2))
    elif operator == "OR":
        operand2 = stack.pop()
        operand1 = stack.pop()
        stack.append(operand1.union(operand2))
    elif operator == "NOT":
        operand2 = stack.pop()
        operand1 = stack.pop()
        stack.append(operand1.difference(operand2))


def precedence(operator):
    # Функция для возвращения приоритета оператора
    if operator == "NOT":
        return 3
    elif operator == "AND":
        return 2
    elif operator == "OR":
        return 1
    else:
        return 0


def boolean_search(query, inverted_index):
    # Функция для выполнения булева поиска
    result = evaluate_expression(query, inverted_index)
    return result


def search():
    filename = 'inverted_index.txt'
    inverted_index = read_data_from_file(filename)

    query = input("Введите запрос: ")
    result = boolean_search(query, inverted_index)

    with open('pages/index.txt', 'r') as file:
        links = file.read().splitlines()
    if result and not (len(result) == 1 and result[0] == '0'):
        print(f"Найденные страницы, содержащие запрос '{query}':")
        for item in result:
            if item != '0':
                print(links[int(item) - 1])
    else:
        print("Ничего не найдено.")


search()
