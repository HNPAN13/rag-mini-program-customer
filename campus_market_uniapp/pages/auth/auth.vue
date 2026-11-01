<template>
  <view class="page">
    <!-- 表单状态（未认证、已驳回，或者点击了修改按钮） -->
    <view class="box" v-if="isEditing">
      <view class="form-item">
        <text>学号</text>
        <input v-model="studentId" placeholder="请输入真实学号" />
      </view>
      <button class="submit-btn" @click="submitAuth">提交认证</button>
      <button class="cancel-btn" v-if="status === 1 || status === 2" @click="isEditing = false">取消修改</button>
    </view>

    <!-- 待审核状态 -->
    <view class="status-box" v-if="!isEditing && status === 1">
      <text class="icon">⏳</text>
      <text class="text">认证审核中</text>
      <text class="tip">您已提交学号：{{ studentId || '已提交' }}，请耐心等待管理员审核</text>

      <!-- 修改按钮 -->
      <button class="modify-btn" @click="isEditing = true">修改认证信息</button>
    </view>

    <!-- 已认证状态 -->
    <view class="status-box" v-if="!isEditing && status === 2">
      <text class="icon">✅</text>
      <text class="text">已认证学生</text>
      <text class="tip">您已解锁发布商品和交易权限</text>

      <!-- 修改按钮 -->
      <button class="modify-btn" @click="isEditing = true">修改认证信息</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

const studentId = ref('')
const status = ref(0)
const isEditing = ref(false) // 控制是否处于编辑状态

onShow(() => {
  // 每次进入页面，从缓存读取状态和学号
  const localStatus = uni.getStorageSync('auth_status') || 0
  status.value = localStatus

  // 如果是第一次进来（未认证或已驳回），直接进入编辑模式
  if (localStatus === 0 || localStatus === 3) {
    isEditing.value = true
  } else {
    isEditing.value = false
  }
})

const submitAuth = () => {
  if (!studentId.value) return uni.showToast({ title: '请输入学号', icon: 'none' })

  const userId = uni.getStorageSync('user_id')
  uni.request({
    url: 'http://127.0.0.1:8000/api/user/auth',
    method: 'POST',
    data: {
      user_id: userId,
      student_id: studentId.value,
      student_card: 'temp.jpg' // 演示阶段传假路径
    },
    success: (res) => {
      if (res.data.code === 0) {
        uni.showToast({ title: '提交成功，等待审核', icon: 'success' })
        status.value = 1 // 状态变为待审核
        isEditing.value = false // 退出编辑模式，展示待审核界面
        uni.setStorageSync('auth_status', 1) // 更新缓存
      }
    }
  })
}
</script>

<style>
.page { padding: 30rpx; background: #f5f5f5; min-height: 100vh; }
.box { background: #fff; padding: 40rpx; border-radius: 12rpx; }
.form-item { margin-bottom: 40rpx; }
.form-item text { display: block; margin-bottom: 20rpx; font-weight: bold; }
.form-item input { border: 1px solid #ddd; padding: 20rpx; border-radius: 8rpx; }
.submit-btn { background: #07c160; color: #fff; border-radius: 40rpx; margin-bottom: 20rpx; }
.cancel-btn { background: #f0f0f0; color: #666; border-radius: 40rpx; }

.status-box { display: flex; flex-direction: column; align-items: center; padding-top: 150rpx; }
.icon { font-size: 100rpx; margin-bottom: 30rpx; }
.text { font-size: 36rpx; font-weight: bold; margin-bottom: 20rpx; }
.tip { font-size: 28rpx; color: #999; margin-bottom: 60rpx; }

/* 修改按钮样式 */
.modify-btn {
  background: #fff;
  color: #07c160;
  border: 1px solid #07c160;
  border-radius: 40rpx;
  font-size: 28rpx;
  padding: 0 40rpx;
}
</style>
