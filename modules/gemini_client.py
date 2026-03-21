"""
Google Gemini APIクライアント
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def get_model():
    """Geminiモデルのシングルトン取得"""
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY が .env に設定されていません")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-2.5-flash")
    return _model


def generate(prompt: str, temperature: float = 0.7) -> str:
    """Gemini APIでテキスト生成"""
    model = get_model()
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4096,
        ),
    )
    return response.text
