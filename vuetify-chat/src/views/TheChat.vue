<template>
  <div class="chat-layout" :class="compactView ? 'compact' : 'full'">
    <!-- Overlay for collapsed panel -->
    <div v-if="leftPanelCollapsed && !compactView" class="overlay" @click="toggleLeftPanel"></div>
    
    <v-row no-gutters class="main-row">
      <!-- LEFT PANEL START -->
      <div v-if="!compactView" class="left-panel" :class="{ 'collapsed': leftPanelCollapsed }">
        <MenuPanel v-show="!compactView" @toggle-panel="toggleLeftPanel" />

        <!-- wait for asynchronous component to load -->
        <!-- https://kaperskyguru.medium.com/exploring-suspense-in-vue-3-9e88c0c4535d -->
        <suspense v-if="isSearch">
          <template #default>
            <ContactsList :style="{ height: 'calc(100vh - 128px)' }" />
          </template>
          <template #fallback>
            <ContactsLoading v-once :style="{ height: 'calc(100vh - 128px)' }" />
          </template>
        </suspense>

        <ChatsList v-if="(isChat && !chatSelected) || (isChat && !compactView)"
          :style="{ height: 'calc(100vh - 128px)' }" />

        <!-- these two appear irrespective of view -->

        <SelectedChatWindow v-if="compactView && isChat && chatSelected" style="height: 600px" />
      </div>
      
      <!-- Compact view menu -->
      <div v-if="compactView" class="compact-menu">
        <MenuPanel />
      </div>

      <!-- LEFT PANEL END -->

      <!-- COLLAPSED PANEL TRIGGER -->
      <div v-if="!compactView && leftPanelCollapsed" class="collapsed-trigger" @click="toggleLeftPanel">
        <v-icon color="white" size="large">mdi-menu</v-icon>
      </div>

      <!-- MAIN CHAT PANEL -->
      <div v-if="!compactView" class="main-panel">
        <SelectedChatWindow v-if="isChat && chatSelected" />
        <EmptyChatWindow v-else-if="isChat && !chatSelected" />
        <EmptySearchWindow v-else-if="isSearch" />
      </div>
      <!-- MAIN PANEL END -->
    </v-row>
    
    <!-- AI RECOMMENDATION PANEL - SEPARATE, CENTERED -->
    <div v-if="!compactView && isChat && chatSelected" class="ai-panel-floating">
      <AIRecommendationPanel />
    </div>
    
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
  </div>
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
.chat-layout {
  position: relative;
  width: 100%;
  height: calc(100vh - 64px); /* Subtract app bar height */
  overflow: hidden;
}

.main-row {
  height: 100%;
  position: relative;
}

/* LEFT PANEL - Telegram style */
.left-panel {
  position: fixed;
  left: 0;
  top: 64px; /* App bar height */
  width: 380px;
  height: calc(100vh - 64px);
  background-color: var(--section-card-background);
  border-right: 1px solid var(--section-card-wrapper);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
  z-index: 1000;
  overflow: hidden;
  border-radius: 0;
}

.left-panel.collapsed {
  transform: translateX(-380px);
}

/* MAIN CHAT PANEL - Constrained width for AI panel */
.main-panel {
  position: fixed;
  left: 380px;
  top: 64px;
  right: 420px;
  height: calc(100vh - 64px);
  background-color: var(--section-card-background);
  transition: left 0.3s ease, right 0.3s ease;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
  border-right: 1px solid var(--section-card-wrapper);
}

.left-panel.collapsed ~ .main-panel {
  left: 0;
}

/* AI PANEL - Fixed right panel */
.ai-panel-floating {
  position: fixed;
  right: 0;
  top: 64px;
  width: 420px;
  height: calc(100vh - 64px);
  background-color: var(--section-card-background);
  border-radius: 0;
  box-shadow: none;
  z-index: 900;
  overflow: hidden;
}

/* Overlay for collapsed state */
.overlay {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  transition: opacity 0.3s ease;
}

/* Collapsed trigger button */
.collapsed-trigger {
  position: fixed;
  left: 16px;
  top: 80px;
  z-index: 1001;
  background-color: var(--navy);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.collapsed-trigger:hover {
  background-color: var(--accent-blue);
  transform: scale(1.1);
}

/* Compact view styles */
.compact-menu {
  width: 100%;
}
</style>
