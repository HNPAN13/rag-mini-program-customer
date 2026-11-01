from fastapi import APIRouter, UploadFile, File
import os
import uuid
from common import success, error

router = APIRouter()


@router.post("/image", summary="上传图片")
async def upload_image(file: UploadFile = File(...)):
    # 1. 校验文件类型
    ext = file.filename.split(".")[-1]
    if ext.lower() not in ["jpg", "jpeg", "png", "gif", "webp"]:
        return error("只允许上传图片格式")

    # 2. 生成唯一文件名（防止重名覆盖）
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join("media", filename)

    # 3. 保存文件
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # 4. 返回 URL 路径
    return success(data={"url": f"/media/{filename}"})