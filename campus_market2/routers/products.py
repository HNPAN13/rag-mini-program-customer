from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Product, Category, ProductImage, User
from schemas import ProductPublishSchema
from common import success, error

router = APIRouter()


@router.get("/categories", summary="获取分类列表")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).order_by(Category.sort_order).all()
    data = [{"id": c.id, "name": c.name} for c in categories]
    return success(data=data)


@router.get("/list", summary="获取商品列表")
def get_products(category_id: int = None, keyword: str = None, db: Session = Depends(get_db)):
    # 默认只查在售商品 (status=1)
    query = db.query(Product).filter(Product.status == 1)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if keyword:
        query = query.filter(Product.title.contains(keyword))

    products = query.all()
    data = []
    for p in products:
        first_img = p.images[0].image if p.images else ''
        data.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "category": p.category.name if p.category else '',
            "seller": p.seller.nickname,
            "image": first_img
        })
    return success(data=data)

@router.get("/{product_id}/detail", summary="获取商品详情")
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return error("商品不存在", 404)

    #获取商品图片
    images = [img.image for img in product.images] if product.images else []

    data = {
        "id": product.id,
        "title": product.title,
        "price": float(product.price),
        "description": product.description,
        "seller": product.seller.nickname,
        "images": images,
        "status": product.status
    }
    return success(data=data)

@router.post("/publish", summary="发布商品")
def publish_product(data: ProductPublishSchema, db: Session = Depends(get_db)):
    # 1. 检查用户是否存在且已认证 (auth_status=2)
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        return error("用户不存在", 404)
    if user.auth_status != 2:
        return error("请先完成学生认证", 403)

    # 2. 创建商品
    new_product = Product(
        title=data.title,
        description=data.description,
        price=data.price,
        category_id=data.category_id,
        seller_id=data.user_id,
        status=1  # 开发阶段直接设为在售，不搞待审核
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 3. 保存商品图片
    for img_url in data.images:
        img = ProductImage(product_id=new_product.id, image=img_url)
        db.add(img)
    db.commit()

    return success(msg="发布成功", data={"product_id": new_product.id})

@router.get("/my/list", summary="我发布的商品")
def get_my_products(user_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.seller_id == user_id).all()
    data = []
    for p in products:
        data.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "status": p.status
        })
    return success(data=data)