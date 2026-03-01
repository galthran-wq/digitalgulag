import { ref } from 'vue'
import { defineStore } from 'pinia'
import { chatStream, listChats, getChat } from '@/api/chat'
import type { ChatMessage, ChatSummary } from '@/types/chat'

let msgSeq = 0
const uid = () => `msg-${Date.now()}-${++msgSeq}`

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const streaming = ref(false)
  const error = ref<string | null>(null)

  // History
  const activeView = ref<'chat' | 'history'>('chat')
  const chatList = ref<ChatSummary[]>([])
  const chatListTotal = ref(0)
  const loadingHistory = ref(false)
  const viewingChatId = ref<string | null>(null)

  let abortController: AbortController | null = null

  async function sendMessage(content: string) {
    if (streaming.value) return
    error.value = null
    viewingChatId.value = null

    messages.value.push({
      id: uid(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    })

    messages.value.push({
      id: uid(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    })
    // Get the reactive proxy so Vue detects mutations during streaming
    const assistantMsg = messages.value[messages.value.length - 1]

    streaming.value = true
    abortController = new AbortController()

    try {
      await chatStream(
        { message: content },
        {
          onText(text) {
            assistantMsg.content += text
          },
          onDone() {},
          onError(err) {
            error.value = err
          },
        },
        abortController.signal,
      )
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        error.value = e.message ?? 'Chat request failed'
        if (!assistantMsg.content) {
          messages.value.splice(messages.value.length - 1, 1)
        }
      }
    } finally {
      streaming.value = false
      abortController = null
    }
  }

  function cancelStream() {
    abortController?.abort()
  }

  function clearMessages() {
    messages.value = []
    error.value = null
    viewingChatId.value = null
  }

  async function fetchHistory() {
    loadingHistory.value = true
    try {
      const res = await listChats(50, 0)
      chatList.value = res.chats
      chatListTotal.value = res.total_count
    } catch (e: any) {
      error.value = e.message ?? 'Failed to load history'
    } finally {
      loadingHistory.value = false
    }
  }

  async function loadChat(chatId: string) {
    loadingHistory.value = true
    try {
      const detail = await getChat(chatId)
      messages.value = detail.messages.map((m) => ({
        id: uid(),
        role: m.role as 'user' | 'assistant',
        content: m.content,
        timestamp: detail.created_at,
      }))
      viewingChatId.value = chatId
      activeView.value = 'chat'
    } catch (e: any) {
      error.value = e.message ?? 'Failed to load chat'
    } finally {
      loadingHistory.value = false
    }
  }

  function newChat() {
    clearMessages()
    activeView.value = 'chat'
  }

  function showHistory() {
    activeView.value = 'history'
    fetchHistory()
  }

  return {
    messages,
    streaming,
    error,
    activeView,
    chatList,
    chatListTotal,
    loadingHistory,
    viewingChatId,
    sendMessage,
    cancelStream,
    clearMessages,
    fetchHistory,
    loadChat,
    newChat,
    showHistory,
  }
})
