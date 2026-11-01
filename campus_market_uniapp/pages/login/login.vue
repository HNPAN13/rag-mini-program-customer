<template>
  <view class="login-page">
    <view class="logo">校园二手</view>
    <view class="tip">正在登录，请稍候...</view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app'

onLoad(() => {
  doLogin()
})

const doLogin = () => {
  uni.login({
    provider: 'weixin',
    success: (res) => {
      uni.request({
        url: 'http://127.0.0.1:8000/api/user/login',
        method: 'POST',
        data: {
          code: res.code,
          nickname: '微信用户'
        },
        success: (resp) => {
          if (resp.data.code === 0) {
            uni.setStorageSync('user_id', resp.data.data.user_id)
            uni.setStorageSync('auth_status', resp.data.data.auth_status)
            uni.switchTab({ url: '/pages/index/index' })
          } else {
            uni.showToast({ title: resp.data.msg, icon: 'none' })
          }
        },
        fail: (err) => {
          console.error('请求失败', err)
          uni.showToast({ title: '连接后端失败', icon: 'none' })
        }
      })
    },
    fail: (err) => {
      console.error('微信登录失败', err)
    }
  })
}
</script>

<style>
.login-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f5f5f5;
}
.logo { font-size: 48rpx; font-weight: bold; color: #07c160; margin-bottom: 30rpx; }
.tip { font-size: 28rpx; color: #999; }
</style>
