import re 
from collections import Counter

class WordFrequencyProcessor:
    def __init__(self):
        self.profiles = {}
    
    def _preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zа-яё\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def create_profile_from_file(self, lang_name: str, file_path: str, profile_size: int = 300):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return
        
        clean_text = self._preprocess_text(text)
        words = clean_text.split()

        if not words:
            return

        word_counts = Counter(words)
        most_common_pairs = word_counts.most_common(profile_size)

        if not most_common_pairs:
            return
        max_freq = most_common_pairs[0][1]

        self.profiles[lang_name] = {word: count / max_freq for word, count in most_common_pairs}

    def detect(self, text: str):
        if not self.profiles:
            return 

        clean_text = self._preprocess_text(text)
        document_words = set(clean_text.split())

        if not document_words:
            return 
        
        scores = {}
        for lang_name, lang_profile in self.profiles.items():
            lang_score = 0
            for word in document_words:
                if word in lang_profile:
                    lang_score += lang_profile[word]
            
            scores[lang_name] = lang_score
        
        for lang, score in scores.items():
            print(f"   Итоговый вес для '{lang}': {score:.4f}")

        if not any(scores.values()):
            return 
        
        best_match = max(scores, key=scores.get)
        return best_match
    
if __name__ == "__main__":
    word_detector = WordFrequencyProcessor()
    
    word_detector.create_profile_from_file("Русский", "train_data/ru_train.txt")
    word_detector.create_profile_from_file("Английский", "train_data/en_train.txt")
    
    print("\n--- Тестирование метода частотных слов ---")
    
    test_text_ru = "Это простой пример текста для проверки работы алгоритма."
    print(f"\nАнализ текста: '{test_text_ru}'")
    result_ru = word_detector.detect(test_text_ru)
    print(f"-> Результат: {result_ru}")
    
    test_text_en = "This is a simple sample text to check how the algorithm works."
    print(f"\nАнализ текста: '{test_text_en}'")
    result_en = word_detector.detect(test_text_en)
    print(f"-> Результат: {result_en}")