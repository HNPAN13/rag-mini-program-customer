<template>
  <view class="page">
    <view class="list">
      <view class="item" v-for="item in products" :key="item.id">
        <view class="info">
          <view class="title">{{ item.title }}</view>
          <view class="price">￥{{ item.price }}</view>
          <view class="status">状态：{{ getStatusText(item.status) }}</view>
        </view>
      </view>
    </view>
    <view v-if="products.length === 0" class="empty">你还没有发布过商品哦</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const products = ref([])

// 状态映射
const getStatusText = (status) => {
  const map = { 0: '待审核', 1: '在售', 2: '已售', 3: '已下架' }
  return map[status] || '未知'
}

onShow(() => {
  const userId = uni.getStorageSync('user_id')
  if (!userId) return

  uni.request({
	url: `http://127.0.0.1:8000/api/product/my/list?user_id=${userId}`,
    success: (res) => {
      if (res.data.code === 0) {
        products.value = res.data.data
      }
    }
  })
})
</script>

<style>
.page { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.item { background: #fff; padding: 30rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.title { font-size: 30rpx; font-weight: bold; margin-bottom: 10rpx; }
.price { font-size: 32rpx; color: #e93b3d; font-weight: bold; margin-bottom: 10rpx; }
.status { font-size: 26rpx; color: #999; }
.empty { text-align: center; color: #999; padding: 100rpx; }
</style>
