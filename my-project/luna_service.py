import os, json, time, random
from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")

if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in .env")

# 新しい Gemini クライアントの初期化
client = genai.Client(api_key=GOOGLE_API_KEY)

# ルナのペルソナと出力フォーマットを固定するシステムプロンプト
SYSTEM_PROMPT = """
You are Luna. Output strictly in 2 blocks: <dialogue> and <game_state_json>.
"""

def generate_with_retry(user_text: str, max_retries=5):
    models = [MODEL_NAME, "gemini-2.0-flash"]
    last_error = None
    for m in models:
        for i in range(max_retries):
            try:
                r = client.models.generate_content(
                    model=m,
                    contents=user_text,
                    config={"system_instruction": SYSTEM_PROMPT}
                )
                return r.text or ""
            except Exception as e:
                last_error = e
                msg = str(e)
                # 429（レート制限）や503（一時的なエラー）の場合、リトライ処理を実行（エキスポネンシャルバックオフ）
                if any(x in msg for x in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]):
                    time.sleep(min(2**i, 20) + random.random())
                    continue
                raise
    raise RuntimeError(f"Model unavailable: {last_error}")

def parse_ai_reply(text: str):
    dialogue = text
    game_state = {}
    # <dialogue> タグから会話テキストを抽出
    if "<dialogue>" in text and "</dialogue>" in text:
        dialogue = text.split("<dialogue>")[1].split("</dialogue>")[0].strip()
    # <game_state_json> タグからJSONデータを抽出・パース
    if "<game_state_json>" in text and "</game_state_json>" in text:
        raw = text.split("<game_state_json>")[1].split("</game_state_json>")[0].strip()
        try:
            game_state = json.loads(raw)
        except:
            game_state = {}
    return dialogue, game_state