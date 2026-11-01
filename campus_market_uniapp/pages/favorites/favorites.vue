<template>
  <view class="page">
    <view class="list">
      <view class="item" v-for="item in favorites" :key="item.id" @click="goDetail(item.id)">
        <view class="info">
          <view class="title">{{ item.title }}</view>
          <view class="price">￥{{ item.price }}</view>
        </view>
      </view>
    </view>
    <view v-if="favorites.length === 0" class="empty">还没有收藏商品哦</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const favorites = ref([])

onShow(() => {
  const userId = uni.getStorageSync('user_id')
  uni.request({
    url: `http://127.0.0.1:8000/api/favorite/my?user_id=${userId}`,
    success: (res) => {
      if (res.data.code === 0) {
        favorites.value = res.data.data
      }
    }
  })
})

const goDetail = (id) => {
  uni.navigateTo({ url: '/pages/detail/detail?id=' + id })
}
</script>

<style>
.page { padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.item { background: #fff; padding: 30rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.title { font-size: 30rpx; margin-bottom: 10rpx; }
.price { font-size: 32rpx; color: #e93b3d; font-weight: bold; }
.empty { text-align: center; color: #999; padding: 100rpx; }
</style>
