from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Product, Review, User
from common import success, error
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ReviewSchema(BaseModel):
    order_id: int
    reviewer_id: int
    rating: int = 5
    content: Optional[str] = ''


@router.post("/create", summary="创建订单")
def create_order(buyer_id: int, product_id: int, db: Session = Depends(get_db)):
    buyer = db.query(User).filter(User.id == buyer_id).first()
    product = db.query(Product).filter(Product.id == product_id).first()

    if not buyer or not product:
        return error("用户或商品不存在", 404)
    if buyer.auth_status != 2:
        return error("请先完成学生认证", 403)
    if product.status != 1:
        return error("商品当前不可购买")
    if product.seller_id == buyer.id:
        return error("不能购买自己的商品")

    # 创建订单
    order = Order(buyer_id=buyer_id, seller_id=product.seller_id, product_id=product_id, status=0)
    db.add(order)

    # 商品状态改为已售 (2)
    product.status = 2

    db.commit()
    db.refresh(order)
    return success(msg="下单成功", data={"order_id": order.id})


@router.get("/my", summary="我的订单")
def get_my_orders(user_id: int, type: str = 'buy', db: Session = Depends(get_db)):
    if type == 'buy':
        orders = db.query(Order).filter(Order.buyer_id == user_id).all()
    else:
        orders = db.query(Order).filter(Order.seller_id == user_id).all()

    data = []
    for o in orders:
        status_map = {0: '待确认', 1: '已完成', 2: '已取消'}
        data.append({
            "id": o.id,
            "product_id": o.product_id,
            "title": o.product.title,
            "price": float(o.product.price),
            "status": o.status,
            "status_text": status_map.get(o.status, '未知')
        })
    return success(data=data)


@router.post("/{order_id}/confirm", summary="确认收货")
def confirm_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return error("订单不存在", 404)

    order.status = 1  # 已完成
    db.commit()
    return success(msg="订单已完成")


@router.post("/review", summary="提交评价")
def create_review(data: ReviewSchema, db: Session = Depends(get_db)):
    if db.query(Review).filter(Review.order_id == data.order_id).first():
        return error("该订单已评价")

    review = Review(
        order_id=data.order_id,
        reviewer_id=data.reviewer_id,
        rating=data.rating,
        content=data.content
    )
    db.add(review)
    db.commit()
    return success(msg="评价成功")