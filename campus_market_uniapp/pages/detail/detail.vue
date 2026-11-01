<template>
  <view class="page" v-if="product">
    <!-- 图片轮播 -->
    <swiper class="swiper" indicator-dots>
      <swiper-item v-for="(img, index) in product.images" :key="index">
        <image :src="'http://127.0.0.1:8000' + img" mode="aspectFill" class="swiper-img" />
      </swiper-item>
      <swiper-item v-if="product.images.length === 0">
        <image src="https://via.placeholder.com/400" mode="aspectFill" class="swiper-img" />
      </swiper-item>
    </swiper>

    <!-- 商品信息 -->
    <view class="info">
      <view class="price">￥{{ product.price }}</view>
      <view class="title">{{ product.title }}</view>
      <view class="desc">{{ product.description || '暂无描述' }}</view>
      <view class="meta">
        <text>卖家：{{ product.seller }}</text>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="btn-fav" :class="{ active: isFav }" @click="toggleFavorite">
        {{ isFav ? '已收藏' : '收藏' }}
      </view>
      <button class="btn-buy" @click="createOrder">立即购买</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

const product = ref(null)
const productId = ref(null)
const isFav = ref(false) // 记录收藏状态

onLoad((options) => {
  productId.value = options.id
  loadDetail()
  checkIsFavorited() // 检查是否已收藏
})

const loadDetail = () => {
  uni.request({
    url: `http://127.0.0.1:8000/api/product/${productId.value}/detail`,
    success: (res) => {
      if (res.data.code === 0) product.value = res.data.data
    }
  })
}

// 检查是否已收藏（简化版：直接查我的收藏列表里有没有这件商品）
const checkIsFavorited = () => {
  const userId = uni.getStorageSync('user_id')
  if (!userId) return
  uni.request({
    url: `http://127.0.0.1:8000/api/favorite/my?user_id=${userId}`,
    success: (res) => {
      if (res.data.code === 0) {
        const list = res.data.data
        // 如果列表里能找到当前商品，说明已收藏
        isFav.value = list.some(item => item.id == productId.value)
      }
    }
  })
}

// 点击收藏/取消收藏
const toggleFavorite = () => {
  const userId = uni.getStorageSync('user_id')
  if (!userId) return uni.showToast({ title: '请先登录', icon: 'none' })

  uni.request({
    url: `http://127.0.0.1:8000/api/favorite/toggle?user_id=${userId}&product_id=${productId.value}`,
    method: 'POST',
    success: (res) => {
      if (res.data.code === 0) {
        isFav.value = res.data.data.favorited // 更新前端状态
        uni.showToast({ title: res.data.msg, icon: 'none' })
      }
    }
  })
}

// 立即购买
const createOrder = () => {
  const userId = uni.getStorageSync('user_id')
  if (!userId) return uni.showToast({ title: '请先登录', icon: 'none' })

  uni.request({
    url: `http://127.0.0.1:8000/api/order/create?buyer_id=${userId}&product_id=${productId.value}`,
    method: 'POST',
    success: (res) => {
      if (res.data.code === 0) {
        uni.showToast({ title: '下单成功', icon: 'success' })
      } else {
        uni.showToast({ title: res.data.msg, icon: 'none' })
      }
    }
  })
}
</script>

<style>
.page { background: #f5f5f5; min-height: 100vh; padding-bottom: 120rpx; }
.swiper, .swiper-img { width: 100%; height: 600rpx; background: #eee; }
.info { background: #fff; padding: 30rpx; }
.price { font-size: 44rpx; color: #e93b3d; font-weight: bold; }
.title { font-size: 34rpx; color: #333; margin: 20rpx 0; }
.desc { font-size: 28rpx; color: #666; margin-bottom: 20rpx; }
.meta { font-size: 26rpx; color: #999; }
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; background: #fff; padding: 20rpx; border-top: 1px solid #eee; }
.btn-fav { flex: 1; text-align: center; padding: 20rpx; background: #f0f0f0; border-radius: 40rpx; margin-right: 20rpx; font-size: 30rpx; }
.btn-fav.active { background: #fff0f0; color: #e93b3d; }
.btn-buy { flex: 2; background: #07c160; color: #fff; border-radius: 40rpx; font-size: 30rpx; margin: 0; }
</style>
