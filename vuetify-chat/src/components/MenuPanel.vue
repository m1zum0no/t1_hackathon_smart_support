<template>
  <v-card color="panel" class="menu-header" elevation="0">
    <div class="d-flex align-center justify-space-between pa-3">
      <div class="d-flex align-center gap-3">
        <v-btn
          v-if="!compactView"
          @click="$emit('toggle-panel')"
          icon
          variant="text"
          size="small"
        >
          <v-icon color="icons">mdi-menu</v-icon>
        </v-btn>
        <v-icon size="large" id="icon-search" color="icons" :class="{ searchTab: isSearch }"
          @click="toggleSearch">mdi-compass
        </v-icon>
        <div style="position: relative;">
          <v-icon id="icon-chats" :class="{ chatsTab: isChat }" size="large" color="icons"
            @click="toggleChat">mdi-chat
          </v-icon>
          <span v-if="totalUnreadMessagesCount" class="unread-badge">
            {{ totalUnreadMessagesCount }}
          </span>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, defineEmits } from "vue";

const emit = defineEmits(['toggle-panel']);

import { storeToRefs } from "pinia";

import { useMainStore } from "@/store/mainStore";
import { useChatStore } from "@/store/chatStore";
import { useMessageStore } from "@/store/messageStore";
import { useUserStore } from "@/store/userStore";
import { useTheme } from 'vuetify'
import { event } from "vue-gtag";

const theme = useTheme();

const router = useRouter();


const chatStore = useChatStore();
const mainStore = useMainStore();
const messageStore = useMessageStore();
const userStore = useUserStore();

const { isSearch, isChat, compactView } = storeToRefs(mainStore);
const { isBottom, totalUnreadMessagesCount } = storeToRefs(chatStore);
const { currentTheme } = storeToRefs(userStore);

// const colorMode = ref("Teal")

const toggleSearch = () => {
  isSearch.value = true;
  isChat.value = false;
  chatStore.removeUnassignedChat();
  messageStore.clearMoreMessagesToLoad();
  isBottom.value = true;
};

const toggleChat = () => {
  isChat.value = true;
  isSearch.value = false;
};



const logout = async () => {
  router.push("/")
  await userStore.logout();
  // reset theme to default 'teal'
  theme.global.name.value = 'teal';
}


const settingsColor = ref("icons")

const settingsSelectedGA = async () => {
  event("settings-selected", {
    event_category: "analytics",
    event_label: "Settings Selected",
    value: 1,
  });
}

const settingsClicked = async () => {
  settingsColor.value = (settingsColor.value === "icons") ? "primary" : "icons";
  await settingsSelectedGA();
};

const clickedOutside = () => {
  settingsColor.value = "teal-lighten-3"
};

const switchTheme = async () => {
  theme.global.name.value = currentTheme.value
  await userStore.setUserTheme(currentTheme.value);
};



</script>

<style scoped>
#icon-search,
#icon-chats,
#icon-settings {
  transition: all 0.2s ease;
  opacity: 0.8;
}

#icon-search:hover,
#icon-chats:hover,
#icon-settings:hover {
  color: var(--accent-blue) !important;
  opacity: 1;
  transform: scale(1.1);
}

.searchTab {
  color: var(--accent-blue) !important;
  opacity: 1;
  animation: rotate 0.5s;
}

.chatsTab {
  color: var(--accent-blue) !important;
  opacity: 1;
  animation: beat 0.5s;
}

.settings-items:hover {
  color: var(--accent-blue);
  cursor: pointer;
}

/* Unread badge styling */
.menu-header {
  height: 64px;
  background-color: #e3e4ed !important;
  border-bottom: 1px solid var(--section-card-wrapper);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  border-radius: 0 !important;
}

.gap-3 {
  gap: 12px;
}

.unread-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background-color: var(--accent-blue);
  color: var(--navy-text);
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

@keyframes beat {
  15%, 85% {
    transform: scale(1.05);
  }
  25%, 75% {
    transform: scale(1.1);
  }
  50% {
    transform: scale(1.15);
  }
}

@keyframes rotate {
  15%, 85% {
    transform: rotate(-0.2turn);
  }
  25%, 75% {
    transform: rotate(-0.4turn);
  }
  50% {
    transform: rotate(-0.6turn);
  }
}
</style>
