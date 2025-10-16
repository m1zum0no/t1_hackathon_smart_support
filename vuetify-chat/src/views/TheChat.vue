<template>
  <v-container style="max-width: 1400px" :class="compactView ? 'pa-0' : ''">
    <v-row no-gutters>
      <!-- LEFT PANEL START -->
      <v-col v-if="!leftPanelCollapsed" class="bg-items rounded-s-lg fill-height" :cols="compactView ? 12 : 3">
        <MenuPanel v-show="!compactView" />

        <!-- wait for asynchronous component to load -->
        <!-- https://kaperskyguru.medium.com/exploring-suspense-in-vue-3-9e88c0c4535d -->
        <suspense v-if="isSearch">
          <template #default>
            <ContactsList :style="compactView ? { height: '540px' } : { height: '640px' }"
              :class="compactView ? '' : 'rounded-bs-lg'" />
          </template>
          <template #fallback>
            <ContactsLoading v-once :style="compactView ? { height: '540px' } : { height: '640px' }" />
          </template>
        </suspense>

        <ChatsList v-if="(isChat && !chatSelected) || (isChat && !compactView)"
          :style="compactView ? { height: '540px' } : { height: '640px' }" :class="compactView ? '' : 'rounded-bs-lg'" />

        <!-- these two appear irrespective of view -->

        <SelectedChatWindow v-if="compactView && isChat && chatSelected" style="height: 600px" />
      </v-col>
      <v-col v-show="compactView">
        <MenuPanel />
      </v-col>

      <!-- LEFT PANEL CHATS END -->

      <!-- COLLAPSE BUTTON -->
      <div v-if="!compactView && isChat && chatSelected" class="collapse-button-container" :style="{ left: leftPanelCollapsed ? '0' : 'calc(25% - 16px)' }">
        <v-btn
          @click="toggleLeftPanel"
          icon
          size="small"
          elevation="2"
          class="collapse-btn"
        >
          <v-icon>{{ leftPanelCollapsed ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
        </v-btn>
      </div>

      <!-- CENTER PANEL START  ONLY FOR LARGE VIEW -->
      <v-col v-if="!compactView" :cols="getCenterPanelCols" class="ma-0 pa-0 chat-panel-height" :class="leftPanelCollapsed ? 'rounded-s-lg' : ''">

        <SelectedChatWindow v-if="isChat && chatSelected" />
        <EmptyChatWindow v-else-if="isChat && !chatSelected" />
        <EmptySearchWindow v-else-if="isSearch" />
      </v-col>
      <!-- CENTER PANEL END -->
      
      <!-- RIGHT AI PANEL START - ONLY FOR LARGE VIEW -->
      <v-col v-if="!compactView && isChat && chatSelected" :cols="getRightPanelCols" class="ma-0 pa-0 chat-panel-height">
        <AIRecommendationPanel />
      </v-col>
      <!-- RIGHT AI PANEL END -->
    </v-row>
    <v-alert v-if="Object.keys(systemMessage).length > 0"
           height="70px"
           :color="alertColor"
           style="position: absolute; bottom: 60%"
           :style="compactView ? 'right: 10%;' : 'right: 30%;'"
           closable
           theme="dark"
           :icon="alertIcon"
           class="mt-3 text-center text-h6 font-weight-bold mx-auto rounded-xl">
    {{ systemMessage.content }}
  </v-alert>
  </v-container>
</template>

<script setup>
import {
  ref,
  onMounted,
  onUnmounted,
  onUpdated,
  defineAsyncComponent,
  computed,
} from "vue";
import { storeToRefs } from "pinia";
import { useTheme } from 'vuetify'

const alertColor = computed(() => {
  switch (systemMessage.value.type) {
    case 'error':
      return 'error';
    case 'success':
      return 'success';
    case 'info':
      return 'info'
    default:
      return 'primary';
  }
});
const alertIcon = computed(() => {
  switch (systemMessage.value.type) {
    case 'success':
      return 'mdi-power-plug';
    case 'error':
      return 'mdi-power-plug-off';
    case 'info':
      return 'mdi-information-variant';
    default:
      return ''; // handle other cases as needed
  }
});
const theme = useTheme();

const ContactsList = defineAsyncComponent(() =>
  import("@/components/ContactsList.vue")
);

import EmptyChatWindow from "@/components/EmptyChatWindow.vue";
import ChatsList from "@/components/ChatsList.vue";
import MenuPanel from "@/components/MenuPanel.vue";

import ContactsLoading from "@/components/ContactsLoading.vue";


import SelectedChatWindow from "@/components/chat/SelectedChatWindow.vue"
import EmptySearchWindow from "@/components/EmptySearchWindow.vue"
import AIRecommendationPanel from "@/components/chat/AIRecommendationPanel.vue"

import { useChatStore } from "@/store/chatStore";
import { useMessageStore } from "@/store/messageStore";
import { useMainStore } from "@/store/mainStore";
import { useWebsocketStore } from "@/store/websocketStore";
import { useUserStore } from "@/store/userStore";

const chatStore = useChatStore();
const messageStore = useMessageStore();
const mainStore = useMainStore();
const websocketStore = useWebsocketStore();
const userStore = useUserStore();

const { chatSelected } = storeToRefs(chatStore);
const { systemMessage } = storeToRefs(messageStore);
const { isSearch, isChat, compactView } = storeToRefs(mainStore);
const { currentUser, currentTheme } = storeToRefs(userStore);


const activeTab = ref(true);
const leftPanelCollapsed = ref(false);

const toggleLeftPanel = () => {
  leftPanelCollapsed.value = !leftPanelCollapsed.value;
};

const getCenterPanelCols = computed(() => {
  if (leftPanelCollapsed.value) {
    return isChat.value && chatSelected.value ? 7 : 12;
  }
  return isChat.value && chatSelected.value ? 5 : 8;
});

const getRightPanelCols = computed(() => {
  return leftPanelCollapsed.value ? 5 : 4;
});




document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    activeTab.value = false;
  } else {
    activeTab.value = true;
  }
});

// important to render appropriate view
compactView.value = window.innerWidth < 700 ? true : false;

onMounted(async () => {
  // Set theme to banking by default if not already set
  if (!currentTheme.value || currentTheme.value === 'teal') {
    currentTheme.value = 'banking';
  }
  theme.global.name.value = currentTheme.value;

  await chatStore.getDirectChats(currentUser.value.userGUID);
  // connect to websocket only if connection does not exist
  if (!websocketStore.socketExists) {
    await websocketStore.connectWebsocket();
    messageStore.displaySystemMessage("success", "Websocket connected", 1000)
  }

  userStore.setEmptyFriendStatuses();

  window.addEventListener("resize", handleWindowChange);
  compactView.value = window.innerWidth < 700 ? true : false;
});

const handleWindowChange = () => {
  // console.log("WIDTH", window.innerWidth, "Available", window.screen.availWidth);
  compactView.value = window.innerWidth < 700 ? true : false;
};

onUpdated(() => {
  console.log("Updated");
});

onUnmounted(() => {
  // must remove event listener(s)
  window.removeEventListener("resize", handleWindowChange);
});
</script>

<style scoped>
.collapse-button-container {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  transition: left 0.3s ease;
}

.collapse-btn {
  background-color: var(--section-card-background) !important;
  color: var(--navy) !important;
  border: 1px solid var(--section-card-wrapper) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}

.collapse-btn:hover {
  background-color: var(--accent-blue) !important;
  color: var(--navy-text) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.chat-panel-height {
  min-height: 700px;
  height: 700px;
}
</style>
