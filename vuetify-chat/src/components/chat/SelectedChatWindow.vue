<template>
  <div class="chat-window-container">
    <ChatBoxHeader />
    <MainChat />
    
    <!-- SEND BUTTON COMPONENT START -->
    <v-card class="rounded-0 input-container">
      <v-row align="end" justify="center" no-gutters class="input-row pa-3">
        <v-textarea 
          ref="textInput" 
          @keydown.enter.prevent="sendMessage" 
          hide-details 
          placeholder="Type your message..." 
          rows="1"
          v-model="messageToSend" 
          auto-grow 
          max-rows="8" 
          variant="solo"
          @input="websocketStore.handleUserTyping"
          :readonly="inputLocked || loadingMessages" 
          class="limited-textarea"
          clearable
          @click:clear="messageToSend = ''"
        ></v-textarea>
        <v-btn 
          @click="sendMessage" 
          icon="mdi-send" 
          variant="text" 
          class="ml-2 send-button"
          :class="messageToSend.trim() === '' ? 'send-button-inactive' : 'send-button-active'"
          size="large"
          :disabled="messageToSend.trim() === ''">
        </v-btn>
      </v-row>
    </v-card>
    <!-- SEND BUTTON COMPONENT END -->
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { storeToRefs } from "pinia";

import MainChat from "@/components/chat/MainChat.vue";
import ChatBoxHeader from "@/components/chat/ChatBoxHeader.vue";

import { useChatStore } from "@/store/chatStore";
import { useWebsocketStore } from "@/store/websocketStore";
import { useMainStore } from "@/store/mainStore";
import { useMessageStore } from "@/store/messageStore";
import { useUserStore } from "@/store/userStore";


const chatStore = useChatStore();
const websocketStore = useWebsocketStore();
const mainStore = useMainStore();
const messageStore = useMessageStore();
const userStore = useUserStore();


const { currentChatGUID, inputLocked } = storeToRefs(chatStore);
const { compactView } = storeToRefs(mainStore);
const { currentUser } = storeToRefs(userStore);
const { currentChatMessages, loadingMessages } = storeToRefs(messageStore);


// Chat box setup, Messages and Chat Functions
const messageToSend = ref("");
const textInput = ref(null);

const sendMessage = async () => {
  if (messageToSend.value.trim() === "") {
    return; // Don't send empty messages
  }
  
  try {
    // Try to send the message
    const success = await websocketStore.sendMessage(messageToSend.value);
    
    if (success) {
      // make input not editable before receive own message via websocket
      inputLocked.value = true;
      // append messages without confirmation from websocket
      currentChatMessages.value.unshift(
        {
          user_guid: currentUser.value.userGUID,
          chat_guid: currentChatGUID.value,
          content: messageToSend.value,
          created_at: new Date(),
          is_read: false,
          is_sending: true,
        }
      );
      // Clear the input field
      messageToSend.value = "";
      // scroll to bottom when own new message is appended (after DOM update)
      nextTick(() => {
        chatStore.scrollToBottom("smooth");
      });
    }
  } catch (error) {
    console.error("Error in sendMessage:", error);
    messageStore.displaySystemMessage("error", "Failed to send message. Please try again.");
  }
}
</script>

<style scoped>
/* Fixed container - prevents dynamic growth */
.chat-window-container {
  position: relative;
  height: calc(100vh - 64px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Input container - fixed at bottom, grows upward */
.input-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  background-color: var(--section-card-wrapper);
  border-top: none;
  box-shadow: none !important;
}

/* Keep buttons aligned to bottom */
.input-row {
  align-items: flex-end !important;
}

.limited-textarea {
  flex: 1;
}

.limited-textarea :deep(.v-field) {
  border-radius: 8px !important;
  background-color: var(--section-card-background);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.limited-textarea :deep(.v-field--focused) {
  box-shadow: 0 2px 6px rgba(74, 144, 226, 0.15);
}

.send-button {
  border-radius: 50% !important;
  transition: all 0.2s ease;
}

.send-button-inactive {
  color: var(--greyed-out-text) !important;
  background-color: transparent !important;
}

.send-button-active {
  color: var(--accent-blue) !important;
  background-color: transparent !important;
}

.send-button-active:hover {
  background-color: rgba(74, 144, 226, 0.1) !important;
  transform: scale(1.05);
}
</style>
