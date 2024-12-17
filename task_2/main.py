import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

def get_text(url):
    """Отримує текстовий вміст за вказаною URL-адресою."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Помилка: {e}")
        return None

# Функція для видалення пунктуації з тексту
def remove_punctuation(text):
    """Видаляє знаки пунктуації з тексту."""
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word):
    """Крок Map: Повертає слово у нижньому регістрі та кількість 1."""
    return word.lower(), 1

def shuffle_function(mapped_values):
    """Крок Shuffle: Групує однакові слова разом."""
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    """Крок Reduce: Підсумовує кількість входжень для кожного слова."""
    key, values = key_values
    return key, sum(values)

def map_reduce(text, search_words=None):
    """Реалізація MapReduce з можливим фільтруванням слів."""
    text = remove_punctuation(text)
    words = text.split()

    # Фільтрація слів, якщо задано search_words
    if search_words:
        words = [word for word in words if word.lower() in search_words]

    with ThreadPoolExecutor() as executor:
        # Паралельний крок Map
        mapped_values = list(executor.map(map_function, words))

    # Крок Shuffle
    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        # Паралельний крок Reduce
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

def visualize_top_words(word_counts, top_n=10):
    """Візуалізує топ N найчастіше вживаних слів за допомогою горизонтальної діаграми."""
    # Сортування слів за частотою та вибір топ N
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)

    # Побудова діаграми
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='skyblue')
    plt.gca().invert_yaxis()  # Інвертація осі Y для зручного читання
    plt.xlabel("Частота")
    plt.ylabel("Слова")
    plt.title(f"Топ {top_n} найчастіше вживаних слів")
    plt.show()

if __name__ == '__main__':
    # URL для отримання тексту (John KEATS)
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)

    if text:
        # Виконання MapReduce для аналізу частоти слів
        word_counts = map_reduce(text)

        # Візуалізація топ 10 слів
        visualize_top_words(word_counts, top_n=10)
    else:
        print("Помилка: Неможливо отримати текстовий вміст.")
