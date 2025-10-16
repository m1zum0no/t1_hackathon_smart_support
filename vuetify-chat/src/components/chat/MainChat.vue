<template>
  <MessagesLoading v-if="loadingMessages" :style="compactView ? { 'height': '450px' } : { 'height': '550px' }" />
  <v-card v-show="!loadingMessages" class="rounded-0" elevation="0">
    <div id="container" ref="chatWindow" :style="{ 'height': 'calc(100vh - 64px - 64px - 90px)' }">
      <div v-for="(message, index) in currentChatMessages" :key="message.message_guid">
        <div v-show="showDateBreak(index)" class="text-center my-3 font-weight-medium date-divider">
          {{ formatDate(message.created_at) }}
          <v-divider class="mt-2 mx-auto border-opacity-50" width="200px" color="secondary" thickness="1px"></v-divider>
        </div>

        <div v-show="earliestUnreadMessageIndex === index" class="unread-divider text-center py-2">
          <p class="text-accent font-weight-medium">Unread messages</p>
        </div>
        <SpeakerBubble v-if="message.user_guid === currentUser.userGUID" class="ml-auto mr-2">
          <v-list-item class="py-1 my-3 text-left bubble-list-item">
            <v-list-item-title class="text-wrap bubble-text">{{
              message.content
            }}</v-list-item-title>

            <v-list-item-subtitle class="mt-1 bubble-timestamp">
              {{ formatTimestamp(message.created_at) }}

              <v-icon v-if="message.is_sending" size="x-small" class="ml-1 text-white">mdi-check</v-icon>
              <v-icon v-else size="x-small" class="ml-1" :class="message.is_read ? 'text-white' : 'text-white'">mdi-check-all</v-icon>
            </v-list-item-subtitle>
          </v-list-item>
        </SpeakerBubble>
        <!-- to scroll to unread messages label: scroll-margin: 50px; -->
        <PartnerBubble v-else style="scroll-margin: 50px;" class="ml-2 partner-msg" :id="message.message_guid"
          :index="index" :message-content="message.content" :message-guid="message.message_guid">
          <v-list-item class="py-1 my-3 ml-2 text-left bubble-list-item">
            <v-list-item-title class="text-wrap bubble-text">{{ message.content }}
            </v-list-item-title>
            <v-list-item-subtitle class="mt-1 bubble-timestamp-partner">
              {{ formatTimestamp(message.created_at) }}
            </v-list-item-subtitle>
          </v-list-item>
        </PartnerBubble>
      </div>
      <v-btn v-if="moreMessagesToLoad" @click="loadMoreMessages" class="mt-3 mx-auto load-more-btn" variant="outlined" color="primary">Load More</v-btn>
    </div>
    <!-- BOTTOM BUTTON FOR SCROLLING / DISPLAYING UNREAD MESSAGES COUNT -->
    <div style="position: absolute;" :style="compactView ? {top: '85%', right: '7%'} : {top: '88%', right: '5%'}">
      <p v-if="!isBottom && chatStore.getUnreadMessagesforChat(currentChatGUID)"
        style="text-align: center; color: rgb(var(--v-theme-scroll)); font-size: 12px; font-weight: bolder;">
        {{ chatStore.getUnreadMessagesforChat(currentChatGUID) }}</p>
      <v-btn v-show="!isBottom" icon class="rounded-circle" @click="chatStore.scrollToBottom('smooth')"
        style="width: 35px; height: 35px;">
        <v-icon size="x-large" color="scroll">mdi-chevron-down</v-icon>
      </v-btn>
    </div>

  </v-card>
</template>


<script setup>
import { onMounted, ref } from "vue";

import PartnerBubble from "@/components/chat/PartnerBubble.vue";
import SpeakerBubble from "@/components/chat/SpeakerBubble.vue";

import { storeToRefs } from "pinia";

import { useUserStore } from "@/store/userStore";
import { useChatStore } from "@/store/chatStore";
import { useMessageStore } from "@/store/messageStore";
import { useObserverStore } from "@/store/observerStore";
import { useMainStore } from "@/store/mainStore";

import MessagesLoading from "@/components/chat/MessagesLoading.vue";


const userStore = useUserStore();
const chatStore = useChatStore();
const messageStore = useMessageStore();
const observerStore = useObserverStore();
const mainStore = useMainStore();
const { compactView } = storeToRefs(mainStore);


const { currentUser } = storeToRefs(userStore);
const { currentChatGUID, isBottom } = storeToRefs(chatStore);
const { currentChatMessages, moreMessagesToLoad, earliestUnreadMessageIndex, loadingMessages } = storeToRefs(messageStore);

import {
  formatTimestamp,
  formatDate,
} from "@/utils/dateUtils";


const chatWindow = ref(null);

const showDateBreak = (index) => {
  const messages = currentChatMessages.value;
  if (index === messages.length - 1) {
    // Always show a date break for the first message
    return true;
  }
  // Compare the date of the current message with the previous message
  const currentDate = new Date(
    currentChatMessages.value[index].created_at
  ).toDateString();
  const nextDate = new Date(
    currentChatMessages.value[index + 1].created_at
  ).toDateString();

  return currentDate !== nextDate;
};

// Function for Loading older messages
const loadMoreMessages = async () => {
  try {
    const lastMessageGUID =
      currentChatMessages.value[currentChatMessages.value.length - 1]["message_guid"];

    const getHistoricalMessagesResponse =
      await messageStore.getHistoricalMessages(
        currentChatGUID.value,
        lastMessageGUID
      );
    // append existing allMessages
    const oldMessages = getHistoricalMessagesResponse.messages;
    oldMessages.forEach((oldMessage) => {
      currentChatMessages.value.push(oldMessage);
    });
    moreMessagesToLoad.value = getHistoricalMessagesResponse.has_more_messages;
  } catch (error) {
    console.error("Error fetching chat history:", error);
    throw error;
  }
};


onMounted(() => {
  // remove old scroll listener and observer
  chatStore.removeWindowScrollHandler();
  observerStore.disconnectObserver();

  chatStore.setChatWindow(chatWindow.value);


  // add new scroll listener and observer
  chatStore.addWindowScrollHandler();
  observerStore.initializeObserver();


});

</script>


<style scoped>
#container {
  overflow: auto;
  display: flex;
  flex-direction: column-reverse;
  background-color: var(--background);
}

.date-divider {
  color: var(--greyed-out-text);
  font-size: 13px;
  letter-spacing: 0.25px;
}

.unread-divider {
  background-color: var(--section-card-wrapper);
  border-radius: 4px;
  margin: 8px 0;
}

.load-more-btn {
  border-color: var(--greyed-out-text) !important;
  color: var(--text) !important;
}

.load-more-btn:hover {
  background-color: var(--hover-bg) !important;
  border-color: var(--accent-blue) !important;
}

/* Styling the scrollbar */
#container::-webkit-scrollbar {
  width: 8px;
}

#container::-webkit-scrollbar-track {
  background-color: var(--background);
}

#container::-webkit-scrollbar-thumb {
  background-color: var(--greyed-out-text);
  border-radius: 4px;
}

#container::-webkit-scrollbar-thumb:hover {
  background-color: var(--navy);
}

/* Bubble list item styling */
.bubble-list-item {
  padding: 0 !important;
  min-height: auto !important;
}

.bubble-text {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-timestamp {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  opacity: 0.9;
}

.bubble-timestamp-partner {
  font-size: 11px;
  color: var(--greyed-out-text);
}
</style>
