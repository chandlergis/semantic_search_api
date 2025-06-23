import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Array<{ text: string; sender: 'user' | 'ai' }>>([])
  const isLoading = ref(false)
  const apiKey = ref(localStorage.getItem('llm_api_key') || '')
  const apiBaseUrl = ref(localStorage.getItem('llm_api_url') || '')
  const selectedModel = ref(localStorage.getItem('llm_model') || 'gpt-3.5-turbo') // 默认模型

  function setApiConfig(key: string, url: string, model: string) {
    apiKey.value = key
    apiBaseUrl.value = url
    selectedModel.value = model
    localStorage.setItem('llm_api_key', key)
    localStorage.setItem('llm_api_url', url)
    localStorage.setItem('llm_model', model)
  }

  async function sendMessage(text: string) {
    if (!apiBaseUrl.value) throw new Error('API URL not configured')
    
    messages.value.push({ text, sender: 'user' })
    isLoading.value = true

    try {
      const response = await fetch(`${apiBaseUrl.value}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey.value}` 
        },
        body: JSON.stringify({
          text,
          model: selectedModel.value // 传递用户选择的模型
        })
      })

      const data = await response.json()
      messages.value.push({ 
        text: data.choices[0].message.content, 
        sender: 'ai' 
      })
    } catch (error) {
      console.error('Chat error:', error)
      messages.value.push({ 
        text: `Error: ${error instanceof Error ? error.message : String(error)}`, 
        sender: 'ai' 
      })
    } finally {
      isLoading.value = false
    }
  }

  return { 
    messages, 
    isLoading, 
    apiKey, 
    apiBaseUrl,
    selectedModel,
    setApiConfig,
    sendMessage 
  }
})