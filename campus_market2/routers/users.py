# routers/users.py
# 用户模块接口：登录、查询用户信息、学生认证
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import LoginRequest, UserInfoResponse, AuthRequest

# 创建路由，统一前缀 /api/users，打标签方便查看文档
router = APIRouter( tags=['用户模块'])


@router.post('/login')
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """微信登录：根据 code 换取 openid，用户不存在则自动注册"""
    # TODO: 正式环境应调用微信 jscode2session 接口用 code 换取真实 openid
    # 这里先用 code 模拟 openid，方便本地开发测试
    openid = "debug_openid_001"  # 必须写死，别用变量

    # 查找用户
    user = db.query(User).filter(User.openid == openid).first()

    # 没有则创建新用户（自动注册）
    if not user:
        user = User(openid=openid, nickname=req.nickname, avatar=req.avatar)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # 已存在则更新昵称、头像
        if req.nickname:
            user.nickname = req.nickname
        if req.avatar:
            user.avatar = req.avatar
        db.commit()
        db.refresh(user)

    return {
        'code': 0,
        'msg': '登录成功',
        'data': {
            'user_id': user.id,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'auth_status': user.auth_status,
        }
    }


@router.get('/', response_model=list[UserInfoResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """查询用户列表（支持分页）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserInfoResponse(user_id=u.id, nickname=u.nickname, auth_status=u.auth_status)
        for u in users
    ]


@router.get('/{user_id}')
def get_user(user_id: int, db: Session = Depends(get_db)):
    """根据 id 查询单个用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='用户不存在')
    return {
        'user_id': user.id,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'student_id': user.student_id,
        'student_card': user.student_card,
        'auth_status': user.auth_status,
        'created_at': user.created_at,
    }


@router.post('/auth')
def submit_auth(req: AuthRequest, db: Session = Depends(get_db)):
    """提交学生认证：学号 + 学生证图片，提交后进入待审核状态"""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='用户不存在')

    # 已认证用户不允许重复提交
    if user.auth_status == 2:
        raise HTTPException(status_code=400, detail='您已完成学生认证')

    user.student_id = req.student_id
    user.student_card = req.student_card
    user.auth_status = 1  # 待审核
    db.commit()
    db.refresh(user)

    return {'msg': '认证申请已提交，请等待审核', 'auth_status': user.auth_status}
