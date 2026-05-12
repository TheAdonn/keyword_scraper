"""
Скрипт для сбора ключевых слов с сайта.
"""

import re
import time
import sys
import requests
from collections import Counter
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

MIN_WORD_LENGTH = 3
DELAY = 0.5
REQUEST_TIMEOUT = 10

STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а",
    "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же",
    "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от",
    "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже",
    "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был",
    "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там",
    "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть",
    "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам",
    "чтоб", "без", "будто", "чего", "раз", "тоже", "себе", "под",
    "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого",
    "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой",
    "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех",
    "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть",
    "после", "над", "больше", "тот", "через", "эти", "нас", "про",
    "всего", "них", "какая", "много", "разве", "три", "эту", "моя",
    "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше",
    "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно",
    "всю", "между", "ваш", "также", "нам", "которые", "которая", "нашем",
    "просто", "это",
    "the", "and", "for", "are", "but", "not", "you", "all", "can",
    "her", "was", "one", "our", "out", "day", "get", "has", "him",
    "his", "how", "man", "new", "now", "old", "see", "two", "way",
    "who", "boy", "did", "its", "let", "put", "say", "she", "too",
    "use", "with", "that", "this", "have", "from", "they", "will",
    "been", "into", "more", "than", "then", "there", "when", "your",
}


def ask_parameters():
    print("=" * 60)
    print("   СБОРЩИК КЛЮЧЕВЫХ СЛОВ С САЙТА")
    print("=" * 60)
    print()

    # START_URL
    while True:
        url = input("Введите адрес сайта (например https://example.com/): ").strip()
        if not url:
            url = "https://example.com/"
            print(f"  Используется по умолчанию: {url}")
        if not url.startswith("http"):
            url = "https://" + url
        break

    print()

    # TOP_N
    while True:
        raw = input("Сколько топовых слов сохранить? (по умолчанию 200): ").strip()
        if not raw:
            top_n = 200
            print(f"  Используется по умолчанию: {top_n}")
            break
        if raw.isdigit() and int(raw) > 0:
            top_n = int(raw)
            break
        print("  Ошибка: введите целое число больше 0")

    print()
    print(f"Сайт:            {url}")
    print(f"Топ слов:        {top_n}")
    print()
    input("Нажмите Enter, чтобы начать анализ...")
    print()

    return url, top_n


def get_all_links(base_url, soup):
    links = set()
    domain = urlparse(base_url).netloc
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc == domain and parsed.scheme in ("http", "https"):
            clean_url = full_url.split("#")[0].rstrip("/")
            links.add(clean_url)
    return links


def extract_text(soup):
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator=" ")


def tokenize(text):
    words = re.findall(r"[а-яёА-ЯЁa-zA-Z]+", text)
    return [
        w.lower() for w in words
        if len(w) >= MIN_WORD_LENGTH and w.lower() not in STOP_WORDS
    ]


def crawl_site(start_url):
    visited = set()
    to_visit = {start_url.rstrip("/")}
    word_counter = Counter()
    crawled_pages = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"Начинаю обход сайта: {start_url}\n")

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue
            if response.status_code != 200:
                print(f"  [!] Пропускаю (статус {response.status_code}): {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            new_links = get_all_links(start_url, soup)
            to_visit.update(new_links - visited)

            text = extract_text(soup)
            words = tokenize(text)
            word_counter.update(words)

            crawled_pages.append(url)
            print(f"  [+] ({len(crawled_pages)}) {url}  —  слов: {len(words)}")

            time.sleep(DELAY)

        except requests.exceptions.RequestException as e:
            print(f"  [!] Ошибка: {url}  —  {e}")

    return word_counter, crawled_pages


def save_results(counter, crawled_pages, start_url, top_n):
    domain = urlparse(start_url).netloc.replace(".", "_")
    output_file = f"keywords_{domain}.txt"
    top_words = counter.most_common(top_n)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"  КЛЮЧЕВЫЕ СЛОВА: {start_url}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Обработано страниц:    {len(crawled_pages)}\n")
        f.write(f"Уникальных слов:       {len(counter)}\n")
        f.write(f"Показаны топ-{top_n}\n\n")
        f.write("-" * 45 + "\n")
        f.write(f"{'№':<5} {'Ключевое слово':<30} {'Частота':>8}\n")
        f.write("-" * 45 + "\n")
        for i, (word, freq) in enumerate(top_words, start=1):
            f.write(f"{i:<5} {word:<30} {freq:>8}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write("СПИСОК ОБРАБОТАННЫХ СТРАНИЦ:\n")
        f.write("=" * 60 + "\n\n")
        for page_url in sorted(crawled_pages):
            f.write(f"  {page_url}\n")

    return output_file


if __name__ == "__main__":
    start_url, top_n = ask_parameters()
    word_counter, crawled_pages = crawl_site(start_url)

    if not crawled_pages:
        print("\nНе удалось обработать ни одной страницы.")
        print("Проверьте адрес сайта и подключение к интернету.")
    else:
        print(f"\nГотово! Обработано страниц: {len(crawled_pages)}")
        print(f"Уникальных слов: {len(word_counter)}")
        output_file = save_results(word_counter, crawled_pages, start_url, top_n)
        print(f"Результаты сохранены в файл: {output_file}")

    print()
    input("Нажмите Enter для выхода...")
