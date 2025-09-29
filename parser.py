import os
import random
import re
import wikipedia

size = 300

ru_filename = "train_data/ru_train.txt"
ru_topics = ["Наука", "Технологии", "Литература"]

en_filename = "train_data/en_train.txt"
en_topics = ["Science", "Technology", "Literature"]

def ru_clean_traslations(text: str) -> str:
    text = text.lower() 
    text = re.sub(r'[^а-яё\s]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def en_clean_traslations(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_ru():
    wikipedia.set_lang("ru")
    if os.path.exists(ru_filename):
        os.remove(ru_filename)
    curr_size = 0 
    while curr_size < size:
        try:
            topic = random.choice(ru_topics)
            search_res = wikipedia.search(topic, results=5)
            if not search_res:
                print("Ничего не найдено, пробую другую тему.")
                continue
            article_title = random.choice(search_res)

            page = wikipedia.page(article_title, auto_suggest=False, redirect=True)

            content = page.content
            cleaned_content = ru_clean_traslations(content)
            with open(ru_filename, "a", encoding="utf-8") as f:
                f.write(cleaned_content + "\n")
            curr_size = os.path.getsize(ru_filename)
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Пропускаю страницу неоднозначности: '{e.title}'")
        except wikipedia.exceptions.PageError as e:
            print(f"Страница не найдена: '{e.title}', пробую следующую.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

def parse_en():
    wikipedia.set_lang("en")
    if os.path.exists(en_filename):
        os.remove(en_filename)
    curr_size = 0 
    while curr_size < size:
        try:
            topic = random.choice(ru_topics)
            search_res = wikipedia.search(topic, results=5)
            if not search_res:
                print("Ничего не найдено, пробую другую тему.")
                continue
            article_title = random.choice(search_res)

            page = wikipedia.page(article_title, auto_suggest=False, redirect=True)

            content = page.summary
            cleaned_content = en_clean_traslations(content)
            with open(en_filename, "a", encoding="utf-8") as f:
                f.write(cleaned_content + "\n")
            curr_size = os.path.getsize(en_filename)
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Пропускаю страницу неоднозначности: '{e.title}'")
        except wikipedia.exceptions.PageError as e:
            print(f"Страница не найдена: '{e.title}', пробую следующую.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == '__main__':
    parse_ru()
    parse_en()