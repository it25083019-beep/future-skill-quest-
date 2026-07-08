from fastapi import FastAPI, HTTPException
from schemas import ChatRequest, CheckinRequest
from store import get_user_state, save_user_state
from exp_engine import add_exp
from luna_service import generate_with_retry, parse_ai_reply

app = FastAPI(title="FSQ Luna Backend")

# ヘルスチェック用エンドポイント
@app.get("/health")
def health():
    return {"ok": True}

# ユーザー状態取得用エンドポイント
@app.get("/state/{user_id}")
def get_state(user_id: str):
    return get_user_state(user_id)

# 朝チェックイン用エンドポイント
@app.post("/checkin/morning")
def morning_checkin(req: CheckinRequest):
    state = get_user_state(req.user_id)
    gain, state = add_exp(state, "morning_checkin")
    state["last_morning_goal"] = req.goal
    save_user_state(req.user_id, state)
    return {"message": "Morning saved", "exp_gain": gain, "state": state}

# 夜チェックイン用エンドポイント
@app.post("/checkin/evening")
def evening_checkin(req: CheckinRequest):
    state = get_user_state(req.user_id)
    gain, state = add_exp(state, "evening_checkin")
    save_user_state(req.user_id, state)
    return {"message": "Evening saved", "exp_gain": gain, "state": state}

# ルナとのチャット用エンドポイント
@app.post("/chat")
def chat(req: ChatRequest):
    state = get_user_state(req.user_id)
    try:
        raw = generate_with_retry(req.message)
        dialogue, ai_state = parse_ai_reply(raw)

        # AIから返ってきた状態の同期処理
        if isinstance(ai_state, dict):
            for k in ["current_focus", "current_plan", "current_do_now", "memory_note"]:
                if k in ai_state:
                    state[k] = ai_state[k]

        # チャット履歴の保存
        state["chat_history"].append({"role": "user", "content": req.message})
        state["chat_history"].append({"role": "assistant", "content": dialogue})
        save_user_state(req.user_id, state)

        return {"dialogue": dialogue, "game_state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))