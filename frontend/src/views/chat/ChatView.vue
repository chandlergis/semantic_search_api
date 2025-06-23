<template>
  <div class="chat-container">
    <!-- API 配置 -->
    
    <!-- 消息列表 -->
    <div class="messages">
      <div 
        v-for="(msg, index) in chatStore.messages" 
        :key="index" 
        :class="['message', msg.sender]"
      >
        {{ msg.text }}
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <input
        v-model="inputText"
        @keyup.enter="send"
        placeholder="Type a message..."
        :disabled="chatStore.isLoading"
      />
      <button @click="send" :disabled="!inputText || chatStore.isLoading">
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { ref } from 'vue'

const chatStore = useChatStore()
const inputText = ref('')

const send = () => {
  if (inputText.value.trim()) {
    chatStore.sendMessage(inputText.value)
    inputText.value = ''
  }
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: #f8f9fa;
}

.config-area {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.config-area input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.config-area button {
  padding: 0.5rem 1rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.message {
  margin: 0.5rem 0;
  padding: 0.75rem;
  border-radius: 8px;
  max-width: 80%;
}
.message.user {
  margin-left: auto;
  background: #007bff;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.message.ai {
  margin-right: auto;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.input-area {
  display: flex;
  gap: 0.5rem;
}
.input-area input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.input-area button {
  padding: 0 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background 0.3s;
}
.input-area button:hover {
  background: #0056b3;
}
</style>