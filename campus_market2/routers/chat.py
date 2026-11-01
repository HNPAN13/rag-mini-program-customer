from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from common import success, error
import httpx
import os

router = APIRouter()

RAG_ASK_URL = "http://127.0.0.1:8001/api/chat/ask"
TIME_OUT = 30

API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL_NAME = "glm-4-flash"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

class ChatRequest(BaseModel):
    message: str


@router.post("/ask", summary="向 AI 客服提问")
def ask_ai(req: ChatRequest):
    try:
        with httpx.Client(timeout=TIME_OUT) as client:
            resp = client.post(
                RAG_ASK_URL,
                json={"message": req.message}
            )
            resp.raise_for_status()
            res_json = resp.json()
        if res_json.get("code") == 0:
            return success(data={"reply": res_json["data"]["reply"]})
        else:
            raise Exception("RAG返回错误")

    except Exception as e:
        print("RAG服务调用失败，降级使用原生大模型：", e)
        # ========== 降级兜底：原来的直接调用智谱逻辑 ==========
        system_prompt = (
            "你是【校园二手交易平台】的智能客服。"
            "你的职责是解答学生用户关于如何发布商品、如何学生认证、如何下单交易的问题。"
            "请用简短、友好、专业的中文回答。不要回答与校园二手交易无关的话题。"
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return success(data={"reply": reply})
