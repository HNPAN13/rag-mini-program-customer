# common.py
# 统一接口返回格式工具函数
from typing import Any


def success(msg: str = 'success', data: Any = None) -> dict:
    """成功返回：{code: 0, msg: ..., data: ...}"""
    return {'code': 0, 'msg': msg, 'data': data}


def error(msg: str = 'error', code: int = 1) -> dict:
    """失败返回：{code: 非0, msg: ..., data: None}"""
    return {'code': code, 'msg': msg, 'data': None}
