<template>
  <div class="chat-window-container">
    <ChatBoxHeader />
    <MainChat />
    
    <!-- SEND BUTTON COMPONENT START -->
    <v-card class="rounded-0 rounded-be-lg input-container">
      <v-row align="end" justify="center" no-gutters class="input-row">
        <!-- @keydown.enter.exact.prevent -> Prevents next line on clicking ENTER -->
        <!-- We should be able to add a new line by pressing SHIFT+ENTER -->
        <!-- @keydown.enter -->
        <v-textarea ref="textInput" @keydown.enter.prevent="sendMessage" hide-details placeholder="Type your text" rows="1"
          v-model="messageToSend" auto-grow max-rows="8" variant="solo" @input="websocketStore.handleUserTyping"
          :readonly="inputLocked || loadingMessages" class="limited-textarea"></v-textarea>

        <v-btn @click="sendMessage" icon="mdi-send" variant="plain" class="ml-0 button-wrapper"
          :color="messageToSend === '' ? 'blue-grey-lighten-2' : 'send'" size="x-large"
          style="font-size: 30px; transform: rotate(-5deg);">
        </v-btn>
      </v-row>

      <v-row class="mb-1 mt-0 ml-5">&nbsp;</v-row>
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
  height: 100%;
  overflow: hidden;
}

/* Input container - fixed at bottom, grows upward */
.input-container {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

/* Keep buttons aligned to bottom */
.input-row {
  align-items: flex-end !important;
}

.button-wrapper {
  align-self: flex-end;
  padding-bottom: 8px;
}

</style>
