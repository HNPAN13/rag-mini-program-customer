<template>
  <view class="page">
    <view class="form-item">
      <text class="label">标题</text>
      <input class="input" placeholder="请输入商品标题" v-model="title" />
    </view>
    <view class="form-item">
      <text class="label">价格</text>
      <input class="input" type="digit" placeholder="请输入价格" v-model="price" />
    </view>
    <view class="form-item">
      <text class="label">描述</text>
      <textarea class="textarea" placeholder="成色、使用情况等" v-model="description" />
    </view>
    <view class="form-item">
      <text class="label">分类</text>
      <picker :range="categories" range-key="name" @change="onCategoryChange">
        <view class="picker">{{ categoryName || '请选择分类' }}</view>
      </picker>
    </view>

    <!-- 图片上传区域 -->
    <view class="form-item">
      <text class="label">商品图片</text>
      <view class="image-list">
        <view class="img-box" v-for="(img, index) in images" :key="index">
          <image :src="img" mode="aspectFill" class="img" />
        </view>
        <view class="img-add" @click="chooseImage">+</view>
      </view>
    </view>

    <button class="submit-btn" @click="submit" :loading="loading">发布商品</button>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('')
const price = ref('')
const description = ref('')
const categories = ref([])
const categoryId = ref(null)
const categoryName = ref('')
const images = ref([]) // 存储本地临时路径
const loading = ref(false)

// 页面加载时获取分类
uni.request({
  url: 'http://127.0.0.1:8000/api/product/categories',
  success: (res) => {
    if (res.data.code === 0) categories.value = res.data.data
  }
})

const onCategoryChange = (e) => {
  const index = e.detail.value
  categoryId.value = categories.value[index].id
  categoryName.value = categories.value[index].name
}

// 选择图片
const chooseImage = () => {
  if (images.value.length >= 3) return uni.showToast({ title: '最多选3张', icon: 'none' })

  uni.chooseImage({
    count: 3 - images.value.length,
    success: (res) => {
      images.value = images.value.concat(res.tempFilePaths)
    }
  })
}

// 上传单张图片到后端
const uploadImage = (filePath) => {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: 'http://127.0.0.1:8000/api/upload/image',
      filePath: filePath,
      name: 'file',
      success: (uploadRes) => {
        const data = JSON.parse(uploadRes.data)
        if (data.code === 0) {
          resolve(data.data.url) // 拿到后端的 "/media/xxx.jpg"
        } else {
          reject(data.msg)
        }
      },
      fail: reject
    })
  })
}

// 提交发布
const submit = async () => {
  const userId = uni.getStorageSync('user_id')
  if (!userId) return uni.showToast({ title: '请先登录', icon: 'none' })
  if (!title.value || !price.value) return uni.showToast({ title: '标题和价格必填', icon: 'none' })

  loading.value = true
  uni.showLoading({ title: '正在上传图片...', mask: true })

  let uploadedUrls = []
  try {
    for (let i = 0; i < images.value.length; i++) {
      const url = await uploadImage(images.value[i])
      uploadedUrls.push(url)
    }
  } catch (err) {
    uni.hideLoading()
    loading.value = false
    return uni.showToast({ title: '图片上传失败', icon: 'none' })
  }

  uni.showLoading({ title: '发布中...', mask: true })
  uni.request({
    url: 'http://127.0.0.1:8000/api/product/publish',
    method: 'POST',
    data: {
      user_id: userId,
      title: title.value,
      price: parseFloat(price.value),
      description: description.value,
      category_id: categoryId.value,
      images: uploadedUrls // 传给后端真实的图片路径
    },
    success: (res) => {
      uni.hideLoading()
      loading.value = false
      if (res.data.code === 0) {
        uni.showToast({ title: '发布成功', icon: 'success' })
        title.value = ''
        price.value = ''
        description.value = ''
        images.value = []
        setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 1000)
      } else {
        uni.showToast({ title: res.data.msg, icon: 'none' })
      }
    },
    fail: () => {
      uni.hideLoading()
      loading.value = false
    }
  })
}
</script>

<style>
.page { padding: 30rpx; background: #f5f5f5; min-height: 100vh; }
.form-item { background: #fff; padding: 24rpx; margin-bottom: 20rpx; border-radius: 12rpx; }
.label { display: block; font-weight: bold; margin-bottom: 16rpx; font-size: 28rpx; }
.input, .textarea, .picker { background: #f8f8f8; padding: 16rpx; border-radius: 8rpx; font-size: 28rpx; }
.textarea { height: 160rpx; }
.submit-btn { background: #07c160; color: #fff; border-radius: 40rpx; margin-top: 40rpx; font-size: 32rpx; }

/* 图片列表样式 */
.image-list { display: flex; flex-wrap: wrap; gap: 20rpx; }
.img-box, .img-add { width: 160rpx; height: 160rpx; border-radius: 8rpx; overflow: hidden; }
.img { width: 100%; height: 100%; }
.img-add { background: #f0f0f0; display: flex; justify-content: center; align-items: center; font-size: 60rpx; color: #999; }
</style>
