from typing import Union
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from underthesea import word_tokenize
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import logging
import unicodedata
import re
from underthesea import word_tokenize, text_normalize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:

    logger.info(f"Loading tokenizer from: vinai/phobert-base-v2")
    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")

    model_path = "hoanoppo001/phobert-finetuned-25k"
    logger.info(f"Loading model from: {model_path}")
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    logger.info("Model loaded successfully!")

except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    # Khởi tạo biến để tránh lỗi
    tokenizer = None
    model = None


def _preprocess_text(text):
    abbrev_map = {
        "k": "không",
        "ko": "không",
        "khong": "không",
        "k0": "không",
        "hok": "không",
        "hem": "không",
        "hong": "không",
        "bt": "bình thường",
        "okie": "ok",
        "oke": "ok",
        "dc": "được",
        "đc": "được",
        "dk": "được",
        "vs": "với",
        "mn": "mọi người",
        "mik": "mình",
        "mk": "mình",
        "nv": "nhân viên",
        "sp": "sản phẩm",
        "bh": "bảo hành",
    }
    if not isinstance(text, str):
        return ""

    # Chuẩn hóa Unicode: NFD → NFC, loại bỏ các khoảng trắng, tab, newline thừa
    text = unicodedata.normalize("NFC", text)

    # Chuẩn hóa chữ thường
    text = text.lower()

    # Chuẩn hoá từ viết tắt (theo dict)
    for abbr, full in abbrev_map.items():
        text = re.sub(rf"\b{abbr}\b", full, text)

    # Chuẩn hóa tiếng Việt (theo underthesea)
    try:
        text = text_normalize(text)
    except Exception:
        pass

    # Loại bỏ dấu câu & ký tự đặc biệt
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Tách từ (word_tokenize từ underthesea)
    tokens = word_tokenize(text, format="text")

    tokens = tokens.split()

    return " ".join(tokens)


def _predict_sentiment(text):
    text = _preprocess_text(text)

    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, padding=True, max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()

    print("Input text:", text)
    print("Xác suất từng nhãn:", probs)
    print("Dự đoán nhãn ID:", pred)

    label_map = {0: "NEGATIVE", 1: "POSITIVE"}
    return label_map[pred]


app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/sentiment/prediction")
def predict_sentiment(input_data: TextInput):
    text = input_data.text
    if text is None or text.strip() == "":
        return {"error": "Input text is empty"}

    sentiment = _predict_sentiment(text)

    return {"text": text, "sentiment": sentiment}
