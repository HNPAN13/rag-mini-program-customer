<template>
  <view class="product-list">
    <view
      class="product-item"
      v-for="item in products"
      :key="item.id"
      @click="goDetail(item.id)"
    >
      <image
        class="img"
        :src="item.image ? 'http://127.0.0.1:8000' + item.image : 'https://via.placeholder.com/200'"
        mode="aspectFill"
      />
      <view class="info">
        <view class="title">{{ item.title }}</view>
        <view class="price">￥{{ item.price }}</view>
        <view class="seller">{{ item.seller }}</view>
      </view>
    </view>
  </view>
  <view v-if="products.length === 0" class="empty">暂无商品</view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const products = ref([])

const loadProducts = () => {
  uni.request({
    url: 'http://127.0.0.1:8000/api/product/list',
    success: (res) => {
      if (res.data.code === 0) {
        products.value = res.data.data
      }
    }
  })
}

onShow(() => {
  loadProducts()
})

const goDetail = (id) => {
  uni.navigateTo({ url: '/pages/detail/detail?id=' + id })
}
</script>

<style>
.product-list { display: flex; flex-wrap: wrap; padding: 20rpx; background: #f5f5f5; min-height: 100vh; }
.product-item { width: 48%; margin: 1%; background: #fff; border-radius: 12rpx; overflow: hidden; }
.img { width: 100%; height: 300rpx; background: #eee; }
.info { padding: 16rpx; }
.title { font-size: 28rpx; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.price { font-size: 32rpx; color: #e93b3d; font-weight: bold; margin: 10rpx 0; }
.seller { font-size: 24rpx; color: #999; }
.empty { text-align: center; color: #999; padding: 100rpx; }
</style>
