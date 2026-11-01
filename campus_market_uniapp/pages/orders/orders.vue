<template>
  <view class="page">
    <view class="tabs">
      <view class="tab" :class="{ active: type === 'buy' }" @click="switchType('buy')">我买到的</view>
      <view class="tab" :class="{ active: type === 'sell' }" @click="switchType('sell')">我卖出的</view>
    </view>

    <view class="order-list">
      <view class="order-item" v-for="item in orders" :key="item.id">
        <view class="info">
          <view class="title">{{ item.title }}</view>
          <view class="price">￥{{ item.price }}</view>
          <view class="status">状态：{{ item.status_text }}</view>
        </view>
        <!-- 只有买家且状态为待确认时，才能确认收货 -->
        <button v-if="type === 'buy' && item.status === 0" class="btn" @click="confirmOrder(item.id)">确认收货</button>
      </view>
    </view>
    <view v-if="orders.length === 0" class="empty">暂无订单</view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const orders = ref([])
const type = ref('buy')

const loadOrders = () => {
  const userId = uni.getStorageSync('user_id')
  uni.request({
    url: `http://127.0.0.1:8000/api/order/my?user_id=${userId}&type=${type.value}`,
    success: (res) => {
      if (res.data.code === 0) {
        orders.value = res.data.data
      }
    }
  })
}

onShow(() => {
  loadOrders()
})

const switchType = (val) => {
  type.value = val
  loadOrders()
}

const confirmOrder = (orderId) => {
  uni.request({
    url: `http://127.0.0.1:8000/api/order/${orderId}/confirm`,
    method: 'POST',
    success: (res) => {
      if (res.data.code === 0) {
        uni.showToast({ title: '已确认收货', icon: 'success' })
        loadOrders()
      }
    }
  })
}
</script>

<style>
.page { background: #f5f5f5; min-height: 100vh; }
.tabs { display: flex; background: #fff; }
.tab { flex: 1; text-align: center; padding: 24rpx; font-size: 30rpx; color: #666; }
.tab.active { color: #07c160; font-weight: bold; border-bottom: 4rpx solid #07c160; }
.order-list { padding: 20rpx; }
.order-item { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 24rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.title { font-size: 30rpx; font-weight: bold; margin-bottom: 10rpx; }
.price { font-size: 32rpx; color: #e93b3d; font-weight: bold; margin-bottom: 10rpx; }
.status { font-size: 26rpx; color: #999; }
.btn { font-size: 26rpx; background: #07c160; color: #fff; border-radius: 30rpx; padding: 0 30rpx; margin: 0; }
.empty { text-align: center; color: #999; padding: 100rpx; }
</style>
