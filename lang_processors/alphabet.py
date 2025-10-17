import re
from collections import Counter
import math


class AlphabetProcessor:
    def __init__(
        self,
        english_path: str = "./train_data/en_train.txt",
        russian_path: str = "./train_data/ru_train.txt",
        other_path: str = "./train_data/other_train.txt",
    ):
        self.profiles = {}
        self.create_profile_from_file("english", english_path)
        self.create_profile_from_file("russian", russian_path)
        self.create_profile_from_file("other", other_path)

    def _preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-zа-яё]", "", text)
        return text

    def create_profile_from_file(self, lang_name: str, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(
                f"ОШИБКА: Не удалось найти файл для языка '{lang_name}' по пути: {file_path}"
            )
            return

        clean_text = self._preprocess_text(text)

        if not clean_text:
            return

        total_letters = len(clean_text)
        letter_counts = Counter(clean_text)
        self.profiles[lang_name] = {
            letter: count / total_letters for letter, count in letter_counts.items()
        }

    def detect(self, text):
        if not self.profiles:
            return
        doc_clean_text = self._preprocess_text(text)
        if not doc_clean_text:
            return

        doc_total_letters = len(doc_clean_text)
        doc_counts = Counter(doc_clean_text)
        doc_profile = {
            letter: count / doc_total_letters for letter, count in doc_counts.items()
        }

        similarities = {}
        all_letters = set(doc_profile.keys())
        for lang_profile in self.profiles.values():
            all_letters.update(lang_profile.keys())

        for lang_name, lang_profile in self.profiles.items():

            dot_product = 0
            norm_doc = 0
            norm_lang = 0

            for letter in all_letters:
                doc_freq = doc_profile.get(letter, 0)
                lang_freq = lang_profile.get(letter, 0)

                dot_product += doc_freq * lang_freq
                norm_doc += doc_freq**2
                norm_lang += lang_freq**2

            if norm_doc == 0 or norm_lang == 0:
                similarity = 0
            else:
                similarity = dot_product / (math.sqrt(norm_doc) * math.sqrt(norm_lang))

            similarities[lang_name] = similarity

        for lang, sim in similarities.items():
            print(f"   Сходство с '{lang}': {sim:.6f}")

        best_match = max(similarities, key=similarities.get)
        return best_match


if __name__ == "__main__":
    detector = AlphabetProcessor()
    detector.create_profile_from_file("Русский", "train_data/ru_train.txt")
    detector.create_profile_from_file("Английский", "train_data/en_train.txt")

    print("\n--- Тестирование ---")
    test_text_ru = "Это простой пример текста для проверки работы алгоритма."
    print(f"\nАнализ текста: '{test_text_ru}'")
    result_ru = detector.detect(test_text_ru)
    print(f"-> Результат: {result_ru}")

    test_text_en = "This is a simple sample text to check how the algorithm works."
    print(f"\nАнализ текста: '{test_text_en}'")
    result_en = detector.detect(test_text_en)
    print(f"-> Результат: {result_en}")
