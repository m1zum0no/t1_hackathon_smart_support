<template>
  <v-card class="rounded-0 chat-header" color="panel" height="60px" :class="compactView ? 'rounded-te-0' : 'rounded-te-lg'">

    <v-card-title class="header-content">

      <div class="d-flex align-center">
        <v-btn icon variant="text" @click="goBack" class="mr-2" size="small">
          <v-icon color="white">mdi-arrow-left</v-icon>
        </v-btn>
        <img v-if="currentFriendImage && !currentFriendImageError" :src="currentFriendImage" class="profile-image"
          :alt="`${currentFriendFirstName}_image`" style="cursor: pointer;" @error="handleImageError()"
          @click="showPhoto = true" />
        <img v-else-if="currentFriendImageError" :src="notAvailablePhotoURL" alt="userImageNotAvailable"
          class="profile-image">
        <img v-else :src="defaultPhotoURL" alt="defaultUserImage" class="profile-image">
        <StatusCircle :friendStatus="friendStatuses[currentFriendGUID]" />
        <!-- Typing status -->
        <span class="ml-2 user-name">{{ currentFriendFirstName }}</span>
        <span v-show="friendTyping" class="typing-indicator ml-2">
            is typing
            <ThreeDots class="ml-n1" />
        </span>
      </div>

      <v-menu :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props" size="large" color="white">mdi-dots-vertical
          </v-icon>
        </template>
        <v-list bg-color="submenu">
          <v-list-item append-icon="mdi-delete" title="Delete Chat" @click="deleteChat(currentChatGUID)">
          </v-list-item>
        </v-list>
      </v-menu>
    </v-card-title>
    <v-dialog width="50%" v-model="showPhoto">
      <img :src="currentFriendImage" :class="compactView ? 'image-enlarged-small' : 'image-enlarged-large'"
        alt="Overlay Image">
    </v-dialog>
  </v-card>
</template>


<script setup>
import { storeToRefs } from "pinia";
import { useChatStore } from "@/store/chatStore";
import { useUserStore } from "@/store/userStore";
import { useMainStore } from "@/store/mainStore";
import { useWebsocketStore } from "@/store/websocketStore";

import { ref, defineAsyncComponent } from "vue";

import StatusCircle from "@/components/StatusCircle.vue";

const ThreeDots = defineAsyncComponent(() => import("@/components/chat/ThreeDots.vue"))

const chatStore = useChatStore();
const userStore = useUserStore();
const mainStore = useMainStore();
const websocketStore = useWebsocketStore();


const { compactView } = storeToRefs(mainStore);
const { friendStatuses, currentTheme } = storeToRefs(userStore);
const { currentFriendUserName, currentFriendFirstName, currentFriendImageError, currentFriendGUID, currentFriendImage, chatSelected, currentChatGUID, friendTyping } = storeToRefs(chatStore);

const ArrowBackImageURL = new URL("@/assets/arrow_back.svg", import.meta.url).href;
const defaultPhotoURL = new URL("@/assets/photo-default.png", import.meta.url).href;
const notAvailablePhotoURL = new URL("@/assets/photo-not-available.png", import.meta.url).href;

const showPhoto = ref(false)

const goBack = () => {
  chatSelected.value = false;
  currentChatGUID.value = null;
  currentFriendImage.value = "";
  currentFriendUserName.value = "";
  currentFriendFirstName.value = "";
  currentFriendGUID.value = "";
  window.document.title = "Ponder Pal: Direct Chats"



}

const handleImageError = () => {
  currentFriendImageError.value = true;
};

const deleteChat = async (chatGUID) => {
  const chatDeleted = await chatStore.deleteDirectChat(chatGUID)
  if (chatDeleted) {
    goBack();
    await websocketStore.sendChatDeleted(chatGUID)
  }
};


</script>

<style scoped>
.chat-header {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px !important;
}

.user-name {
  color: var(--navy-text);
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.25px;
}

.typing-indicator {
  color: var(--navy-text);
  font-size: 13px;
  opacity: 0.9;
  font-style: italic;
}

.image-enlarged-large {
  border-radius: 50%;
  width: 500px;
  height: 500px;
  object-fit: cover;
}

.image-enlarged-small {
  border-radius: 50%;
  width: 300px;
  height: 300px;
  object-fit: cover;
  position: absolute;
  bottom: 0;
  left: -25%;
}
</style>