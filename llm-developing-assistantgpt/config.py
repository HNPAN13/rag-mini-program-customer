import os
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
load_dotenv()

# 获取智谱API密钥
ZHIPUAI_API_KEY = os.environ['ZHIPUAI_API_KEY']

# 智谱模型列表
MODELS = [
    "glm-4-flash",   # 免费，速度快，毕设强烈推荐
    "glm-4",         # 旗舰，效果更好，消耗额度
    "glm-3-turbo"
]
DEFAULT_MODEL = MODELS[0]

# 模型最大token映射
MODEL_TO_MAX_TOKENS = {
    "glm-4-flash": 128000,
    "glm-4": 128000,
    "glm-3-turbo": 128000,
}

# 文本切片参数（保留不变）
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

DEFAULT_MAX_TOKENS = 2000
