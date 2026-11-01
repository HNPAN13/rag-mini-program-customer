from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from AssistantGPT import AssistantGPT
from loguru import logger
# 导入你本地写好的Qdrant类
from db_qdrant import Qdrant

app = FastAPI(title="RAG知识库微服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 固定集合名 test
COLLECTION_NAME = "8d78afaa952ae9154fc537f8f506096e"
# 实例化Qdrant（自动读取 ./qdrant_data 本地库，和Gradio共用同一个向量库！）
qdrant = Qdrant()


class AskReq(BaseModel):
    message: str


@app.post("/api/chat/ask")
async def ask_rag(req: AskReq):
    try:
        user_question = req.message
        top_n = 20

        # ========= 调用和Gradio一模一样的embedding！ =========
        # 注意：你项目里面，生成向量的逻辑在 build_chat_document_prompt 内部
        # 我们直接复用AssistantGPT里面获取embedding的逻辑
        gpt = AssistantGPT()
        # 这里就是文本转向量，和上传文档入库用的同一个embedding接口！
        embedding_vector = gpt.get_embeddings(user_question)[0]

        # ========= 检索test集合 =========
        search_result = qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding_vector,
            limit=top_n
        )

        # ========= 拼接上下文！注意字段是 page_content =========
        context_list = []
        for point in search_result:
            chunk_text = point.payload.get("page_content", "")
            if chunk_text.strip():
                context_list.append(chunk_text)
        retrieval_context = "\n\n".join(context_list)

        logger.info(f"【用户提问】{user_question}")
        logger.info(f"【召回片段数量】{len(search_result)}")
        logger.info(f"【召回上下文】\n{retrieval_context}")

        # ========= 手动构造RAG提示词 =========
        user_prompt = f"""
你是文档问答助手，请严格只根据下面的参考资料回答问题。
如果参考资料没有相关内容，请直接回复：知识库中没有该信息，不要自己编造答案。

【参考资料】
{retrieval_context}

【用户问题】
{user_question}
"""

        messages = [{"role": "user", "content": user_prompt}]
        reply = gpt.get_completion(
            messages=messages,
            model="glm-4-flash",
            max_tokens=1000,
            temperature=0.7,
            stream=False
        )
        return {"code": 0, "msg": "ok", "data": {"reply": reply}}

    except Exception as e:
        logger.exception("RAG接口异常")
        return {"code": -1, "msg": "RAG内部错误", "data": {"reply": ""}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_api:app", host="0.0.0.0", port=8001, reload=True)
