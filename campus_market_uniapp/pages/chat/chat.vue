<template>
  <view class="chat-container">
    <!-- 聊天记录区域 -->
    <scroll-view class="chat-list" scroll-y :scroll-top="scrollTop">
      <view class="msg-item" :class="item.role === 'user' ? 'user' : 'bot'" v-for="(item, index) in messages" :key="index">
        <view class="avatar">{{ item.role === 'user' ? '👤' : '🤖' }}</view>
        <view class="bubble">{{ item.content }}</view>
      </view>
    </scroll-view>

    <!-- 底部输入区域 -->
    <view class="input-area">
      <input class="msg-input" v-model="inputText" @confirm="sendMessage" placeholder="请输入您的问题..." />
      <button class="send-btn" @click="sendMessage">发送</button>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const inputText = ref('')
const scrollTop = ref(0)
const messages = ref([
  { role: 'bot', content: '您好，我是校园二手AI助手。请问有什么可以帮您？\n您可以问我：怎么发布商品？如何退款？认证要多久？' }
])

// 预置的本地知识库（模拟 Agent）
const knowledgeBase = [
  { keys: ['发布', '卖', '怎么发'], reply: '您可以在底部导航栏点击“发布”，填写商品标题、价格、描述并上传图片即可发布。注意，需要先完成学生认证哦！' },
  { keys: ['认证', '学号', '审核'], reply: '点击“我的” -> “学生认证”，输入真实学号提交。管理员审核通过后即可解锁全部交易权限。' },
  { keys: ['买', '下单', '购买'], reply: '在首页点击您心仪的商品进入详情页，点击“立即购买”即可下单。目前仅支持线下当面交易。' },
  { keys: ['退款', '退货'], reply: '由于是校园二手当面交易，平台暂不支持线上退款。建议您在购买前仔细核对商品状态，如遇纠纷请联系管理员。' },
  { keys: ['你好', '在吗', 'hi'], reply: '您好！我在的，有什么可以帮您？' }
]

// 发送消息
const sendMessage = () => {
  const text = inputText.value.trim()
  if (!text) return

  // 1. 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  // 2. 显示加载中
  uni.showLoading({ title: 'AI思考中...', mask: true })

  // 3. 请求后端 AI 接口
  uni.request({
    url: 'http://127.0.0.1:8000/api/chat/ask',
    method: 'POST',
    data: { message: text },
    success: (res) => {
      uni.hideLoading()
      if (res.data.code === 0) {
        messages.value.push({ role: 'bot', content: res.data.data.reply })
      } else {
        messages.value.push({ role: 'bot', content: '接口报错了，请检查后端。' })
      }
      scrollToBottom()
    },
    fail: () => {
      uni.hideLoading()
      messages.value.push({ role: 'bot', content: '网络连接失败。' })
      scrollToBottom()
    }
  })
}
// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    scrollTop.value = 99999 // 强行滚到底部
  })
}
</script>

<style>
.chat-container { display: flex; flex-direction: column; height: 100vh; background: #f5f5f5; }
.chat-list { flex: 1; padding: 30rpx; box-sizing: border-box; overflow: hidden; }
.msg-item { display: flex; margin-bottom: 40rpx; }
.msg-item.user { flex-direction: row-reverse; }
.avatar { width: 80rpx; height: 80rpx; border-radius: 50%; background: #fff; display: flex; justify-content: center; align-items: center; font-size: 40rpx; flex-shrink: 0; }
.bubble { max-width: 70%; padding: 20rpx 30rpx; border-radius: 20rpx; font-size: 28rpx; line-height: 1.5; word-break: break-all; }
.msg-item.bot .bubble { background: #fff; margin-left: 20rpx; border-top-left-radius: 0; color: #333; }
.msg-item.user .bubble { background: #07c160; margin-right: 20rpx; border-top-right-radius: 0; color: #fff; }

.input-area { display: flex; padding: 20rpx; background: #fff; border-top: 1px solid #eee; padding-bottom: env(safe-area-inset-bottom); }
.msg-input { flex: 1; background: #f5f5f5; border-radius: 40rpx; padding: 0 30rpx; height: 70rpx; font-size: 28rpx; }
.send-btn { width: 140rpx; height: 70rpx; line-height: 70rpx; background: #07c160; color: #fff; border-radius: 40rpx; margin-left: 20rpx; font-size: 28rpx; padding: 0; }
</style>
