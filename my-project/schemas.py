from pydantic import BaseModel
from typing import Optional, Dict, Any

# チャットリクエストのデータ構造
class ChatRequest(BaseModel):
    user_id: str
    message: str

# チェックイン（リクエスト）のデータ構造
class CheckinRequest(BaseModel):
    user_id: str
    goal: Optional[str] = None

# チャットレスポンスのデータ構造
class ChatResponse(BaseModel):
    dialogue: str
    game_state: Dict[str, Any]