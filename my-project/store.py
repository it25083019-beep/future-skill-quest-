from typing import Dict, Any

# メモリ上の擬似データベース（サーバー再起動でリセットされます）
DB: Dict[str, Dict[str, Any]] = {}

def get_user_state(user_id: str) -> Dict[str, Any]:
    # 新規ユーザーの場合、初期状態（デフォルト値）を設定
    if user_id not in DB:
        DB[user_id] = {
            "user_id": user_id,
            "current_level": 1,
            "total_exp": 0,
            "daily_exp": 0,
            "streak": 0,
            "chat_history": [],
            "trained_knowledge": []
        }
    return DB[user_id]

def save_user_state(user_id: str, state: Dict[str, Any]):
    # ユーザー状態の保存・更新
    DB[user_id] = state