<template>
  <view class="page">
    <view class="header">
      <view class="avatar">👤</view>
      <view class="info">
        <view class="name">微信用户</view>
        <view class="status">{{ authStatus === 2 ? '已认证学生' : '未认证' }}</view>
      </view>
    </view>

    <view class="menu">
      <view class="menu-item" @click="goPage('/pages/myProducts/myProducts')">
        <text>我的发布</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goPage('/pages/favorites/favorites')">
        <text>我的收藏</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goPage('/pages/orders/orders')">
        <text>我的订单</text>
        <text class="arrow">›</text>
      </view>
      <view class="menu-item" @click="goPage('/pages/auth/auth')">
        <text>学生认证</text>
        <text class="arrow">›</text>
      </view>
	   <!-- 新增的联系客服按钮 -->
	  <view class="menu-item" @click="goPage('/pages/chat/chat')">
	    <text>联系客服</text>
	    <text class="arrow">›</text>
	  </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const authStatus = ref(0)

onShow(() => {
  authStatus.value = uni.getStorageSync('auth_status') || 0
})

// 跳转页面函数
const goPage = (url) => {
  uni.navigateTo({ url })
}
</script>

<style>
.page { background: #f5f5f5; min-height: 100vh; }
.header { background: #07c160; padding: 60rpx 40rpx; display: flex; align-items: center; }
.avatar { width: 120rpx; height: 120rpx; background: rgba(255,255,255,0.3); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 60rpx; }
.info { margin-left: 30rpx; color: #fff; }
.name { font-size: 36rpx; font-weight: bold; }
.status { font-size: 24rpx; margin-top: 10rpx; background: rgba(0,0,0,0.2); padding: 4rpx 16rpx; border-radius: 20rpx; display: inline-block; }
.menu { margin-top: 20rpx; background: #fff; }

.menu-item {
  padding: 30rpx 40rpx;
  border-bottom: 1px solid #f0f0f0;
  font-size: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.arrow { color: #ccc; font-size: 32rpx; }
</style>
