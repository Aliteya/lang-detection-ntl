import torch
import joblib
import json


class NeuroLangProcessor(torch.nn.Module):
    def __init__(self, input_size: int, classes: int):
        super().__init__()
        self.layer_1 = torch.nn.Linear(in_features=input_size, out_features=256)
        self.hidden = torch.nn.ReLU()
        self.layer_2 = torch.nn.Linear(in_features=256, out_features=classes)

    def forward(self, x):
        out = self.layer_1(x)
        out = self.hidden(out)
        out = self.layer_2(out)
        return out


class NeuroProccessor:
    def __init__(
        self,
        vectorizer_path="./lang_processors/tfidf_vectorizer.pkl",
        neuro_path="./lang_processors/neurolang_processor_model.pth",
    ):
        self.vectorizer = joblib.load(vectorizer_path)
        with open("./lang_processors/lang_labels_map.json", "r", encoding="utf-8") as f:
            self.code_to_label_map = json.load(f)
        input_size = self.vectorizer.max_features
        num_of_classes = len(self.code_to_label_map)
        self.neuro = NeuroLangProcessor(input_size=input_size, classes=num_of_classes)
        self.neuro.load_state_dict(torch.load(neuro_path))
        self.neuro.eval()

    def detect(self, text: str) -> str:
        processed_text = text.lower()

        vectorized_text_sparse = self.vectorizer.transform([processed_text])
        vectorized_text_dense = vectorized_text_sparse.toarray()
        text_tensor = torch.tensor(vectorized_text_dense, dtype=torch.float32)

        with torch.no_grad():
            logits = self.neuro(text_tensor)
            predicted_index = torch.argmax(logits, dim=1).item()

        return self.code_to_label_map.get(str(predicted_index), "Неизвестный класс")


test_sentence = "Me gustas tu"
neu_proc = NeuroProccessor()
predicted_lang = neu_proc.detect(test_sentence)

print(f"Текст: '{test_sentence}'\nПредсказанный язык: {predicted_lang}")
