from fastapi import FastAPI, Request, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from collections import Counter
import io
import time
from lang_processors import AlphabetProcessor, WordFrequencyProcessor, NeuroProccessor
from bs4 import BeautifulSoup


def html_parsing(content):
    soup = BeautifulSoup(content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text_to_process = soup.get_text(separator=" ", strip=True)
    return text_to_process


alphabet_processor = AlphabetProcessor()
frequency_processor = WordFrequencyProcessor()
neuro_processor = NeuroProccessor()

app = FastAPI(version="v1")
templates = Jinja2Templates(directory="templates")

analysis_history = []


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": analysis_history,
            "summary": get_summary_stats(),
        },
    )


@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})


@app.post("/api/{processor_type}/", response_class=HTMLResponse)
async def process_text(
    request: Request,
    processor_type: str,
    text_input: str = Form(None),
    file_input: UploadFile = None,
):
    doc_url = f"/document/analysis_{int(time.time())}"

    processor = None
    processor_name = ""
    if processor_type == "alphabet":
        processor = alphabet_processor
        processor_name = "Анализ частоты букв (Косинусное сходство)"
    elif processor_type == "frequency":
        processor = frequency_processor
        processor_name = "Анализ частоты слов (Взвешенный счет)"
    elif processor_type == "neuro":
        processor = neuro_processor
        processor_name = "Нейросетевой анализ (TF-IDF + Нейросеть)"
    else:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Неизвестный тип процессора.",
                "results": analysis_history,
                "summary": get_summary_stats(),
            },
        )

    text_to_process = ""
    if file_input is not None:
        content = await file_input.read()
        text_to_process = html_parsing(content)
    elif text_input:
        text_to_process = text_input
    else:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Нет текста для обработки.",
                "results": analysis_history,
                "summary": get_summary_stats(),
            },
        )

    print(f"Запуск {processor_name} для текста: {text_to_process[:50]}...")
    identified_language = processor.detect(text_to_process)
    result_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "processor": processor_name,
        "document_link": doc_url,
        "text_snippet": text_to_process[:100]
        + ("..." if len(text_to_process) > 100 else ""),
        "detected_language": (
            identified_language if identified_language else "Не определен"
        ),
        "raw_text": text_to_process,
    }
    analysis_history.append(result_data)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": analysis_history,
            "summary": get_summary_stats(),
        },
    )


def get_summary_stats():
    """Рассчитывает сводную статистику по всем обработанным текстам."""
    if not analysis_history:
        return {"total_texts": 0, "language_distribution": {}}

    total_texts = len(analysis_history)
    lang_counts = Counter([item["detected_language"] for item in analysis_history])

    distribution = {
        lang: f"{count} ({count / total_texts * 100:.2f}%)"
        for lang, count in lang_counts.items()
    }

    return {"total_texts": total_texts, "language_distribution": distribution}


@app.get("/download_results/", response_class=StreamingResponse)
async def download_results():
    output = io.StringIO()
    output.write("--- Результаты идентификации языка ---\n\n")

    summary = get_summary_stats()
    output.write(f"Сводная статистика (Всего текстов: {summary['total_texts']}):\n")
    for lang, count_perc in summary["language_distribution"].items():
        output.write(f"- {lang}: {count_perc}\n")
    output.write("\n" + "=" * 50 + "\n\n")

    output.write("Детальная история анализа:\n")
    for i, result in enumerate(analysis_history, 1):
        output.write(f"--- Результат #{i} ---\n")
        output.write(f"Время: {result['timestamp']}\n")
        output.write(f"Метод: {result['processor']}\n")
        output.write(f"Ссылка (имитация): {result['document_link']}\n")
        output.write(f"Определенный язык: {result['detected_language']}\n")
        output.write(f"Фрагмент текста: {result['text_snippet']}\n")
        output.write("-" * 20 + "\n")

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.read().encode("utf-8")),
        media_type="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=lang_detection_results.txt"
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
