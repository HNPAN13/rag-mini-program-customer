# main.py
import os.path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from routers import users, products,upload,favorites,orders,chat

app = FastAPI(title='校园二手交易平台 API')

#确保media文件存在
if not os.path.exists("media"):
    os.makedirs("media")

# 挂载静态文件目录、
app.mount("/media",StaticFiles(directory="media"),name="media")

# 注册用户路由
app.include_router(users.router, prefix='/api/user', tags=['用户模块'])

# 注册商品路由
app.include_router(products.router, prefix='/api/product', tags=['商品模块'])
#上传图片路由
app.include_router(upload.router, prefix='/api/upload', tags=['上传模块'])
#收藏路由
app.include_router(favorites.router, prefix='/api/favorite', tags=['收藏模块'])
#订单模块路由
app.include_router(orders.router, prefix='/api/order', tags=['订单模块'])
## ... 挂载其他路由 ...
app.include_router(chat.router, prefix="/api/chat", tags=["AI客服模块"])

@app.get('/')
def root():
    return {'msg': 'FastAPI 服务已启动'}