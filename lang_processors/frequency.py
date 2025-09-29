import re 
from collections import Counter

class WordFrequencyProcessor:
    def __init__(self):
        self.profiles = {}
    
    def _preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub()