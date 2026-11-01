from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Favorite, Product
from common import success, error

router = APIRouter()

@router.post("/toggle", summary="收藏/取消收藏")
def toggle_favorite(user_id: int, product_id: int, db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.product_id == product_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return success(msg="已取消收藏", data={"favorited": False})
    else:
        new_fav = Favorite(user_id=user_id, product_id=product_id)
        db.add(new_fav)
        db.commit()
        return success(msg="收藏成功", data={"favorited": True})

@router.get("/my", summary="我的收藏")
def get_my_favorites(user_id: int, db: Session = Depends(get_db)):
    favs = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    data = []
    for f in favs:
        p = f.product
        data.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "image": p.images[0].image if p.images else ''
        })
    return success(data=data)