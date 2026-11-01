# schemas.py
from pydantic import BaseModel
from typing import List, Optional


# --- 用户模块 ---

class LoginRequest(BaseModel):
    """登录请求参数"""
    code: str
    nickname: str = '微信用户'
    avatar: str = ''

class UserInfoResponse(BaseModel):
    """用户信息返回结构（示意，实际返回用 dict 也行）"""
    user_id: int
    nickname: str
    auth_status: int

class AuthRequest(BaseModel):
    """学生认证请求参数"""
    user_id: int
    student_id: str
    student_card: str = ''

# 发布商品数据
class ProductPublishSchema(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = ''
    price: float
    category_id: int
    images: List[str] = []  # 接收图片路径列表