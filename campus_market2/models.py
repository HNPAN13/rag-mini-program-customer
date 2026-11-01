# models.py
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True)
    nickname = Column(String(32), default='')
    avatar = Column(String(255), default='')
    student_id = Column(String(20), default='')
    student_card = Column(String(255), default='')
    auth_status = Column(Integer, default=0)  # 0未认证 1待审核 2已认证 3已驳回
    created_at = Column(DateTime, server_default=func.now())


class Category(Base):
    """商品分类表"""
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    sort_order = Column(Integer, default=0)


class Product(Base):
    """商品表"""
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(64), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id', ondelete='SET NULL'))
    seller_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status = Column(Integer, default=0)  # 0待审核 1在售 2已售 3已下架
    created_at = Column(DateTime, server_default=func.now())

    # 关系：方便通过 product.seller 直接拿到卖家对象
    seller = relationship('User')
    category = relationship('Category')
    images = relationship('ProductImage', cascade='all, delete-orphan')


class ProductImage(Base):
    """商品图片表"""
    __tablename__ = 'product_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    image = Column(String(255), nullable=False)


class Order(Base):
    """订单表"""
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    seller_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    status = Column(Integer, default=0)  # 0待确认 1已完成 2已取消
    created_at = Column(DateTime, server_default=func.now())

    buyer = relationship('User', foreign_keys=[buyer_id])
    seller = relationship('User', foreign_keys=[seller_id])
    product = relationship('Product')


class Review(Base):
    """评价表"""
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id', ondelete='CASCADE'), unique=True, nullable=False)
    reviewer_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, default=5)
    content = Column(String(255), default='')
    created_at = Column(DateTime, server_default=func.now())

    reviewer = relationship('User')
    order = relationship('Order')


class Favorite(Base):
    """收藏表"""
    __tablename__ = 'favorite'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User')
    product = relationship('Product')