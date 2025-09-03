<template>
  <div class="settings-view" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);">
    <h2>设置</h2>
    
    <el-form label-position="top" class="settings-form" style="display: flex; justify-content: space-between;">
      <el-form-item label="LLM API URL">
        <el-input 
          v-model="apiUrl" 
          placeholder="http://localhost:5000/v1"
        />
      </el-form-item>
      
      <el-form-item label="API Key">
        <el-input 
          v-model="apiKey" 
          type="password"
          placeholder="输入您的API密钥"
          show-password
        />
      </el-form-item>

      <el-form-item label="模型名称">
        <el-input 
          v-model="selectedModel" 
          placeholder="输入模型名称"
        />
      </el-form-item>
      
      <el-form-item style="margin-left: auto;">
        <el-button 
          type="primary" 
          @click="saveSettings"
        >
          保存设置
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat';
import { ElMessage } from 'element-plus';

import { storeToRefs } from 'pinia';

const chatStore = useChatStore();
const { apiBaseUrl: apiUrl, apiKey, selectedModel } = storeToRefs(chatStore);

const saveSettings = () => {
  chatStore.setApiConfig(apiKey.value, apiUrl.value, selectedModel.value);
  ElMessage.success('设置已保存');
};
</script>

<style scoped>
.settings-view {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
}

.settings-form {
  margin-top: 2rem;
}
</style>