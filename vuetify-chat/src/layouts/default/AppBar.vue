<template>
  <v-app-bar id="app-bar" color="appbar" v-if="isSearch || !compactView || compactView&&!chatSelected" class="full-width-bar app-bar-shadow">
    <router-link :to="{ name: 'Chat' }" style="text-decoration: none; color: inherit" class="ml-2">
      <v-app-bar-title>
        <v-icon icon="mdi-chat" color="logoleft" style="z-index: 1;" />
        <v-icon icon="mdi-chat" color="logoright" style="transform: scaleX(-1);" class="ml-n5" />

        <span class="mx-2 text-gray font-weight-bold" style="user-select: none;">T1 Smart Support</span>
      </v-app-bar-title>
    </router-link>

    <div class="ml-auto" style="font-family: Sriracha">

      <div v-if="isLoggedIn" class="menu">
        <router-link class="link header-link" @click="logoutAndRedirect" to="/">Logout</router-link>
      </div>

      <div v-else class="menu">
        <router-link class="link header-link" :to="{ name: 'Login' }">Login</router-link>
        <router-link class="link header-link mr-5" :to="{ name: 'Register' }">Register</router-link>
      </div>

    </div>

  </v-app-bar>
</template>

<script setup>
import { storeToRefs } from "pinia";
import { useUserStore } from "@/store/userStore";
import { useMainStore } from "@/store/mainStore";
import { useChatStore } from "@/store/chatStore";
import { useRouter } from "vue-router";
import { ref } from "vue";
import { useTheme } from 'vuetify'

const router = useRouter();
const userStore = useUserStore();
const mainStore = useMainStore();
const chatStore = useChatStore();


const { isLoggedIn, currentUser } = storeToRefs(userStore);
const { compactView, isChat, isSearch } = storeToRefs(mainStore);
const { chatSelected } = storeToRefs(chatStore);

const defaultPhotoURL = new URL("@/assets/photo-default.png", import.meta.url).href;
const notAvailablePhotoURL = new URL("@/assets/photo-not-available.png", import.meta.url).href;
const userImageError = ref(false);

const theme = useTheme();

const logoutAndRedirect = async () => {
  router.push("/")
  await userStore.logout()
  // reset theme to default 'teal'
  theme.global.name.value = 'teal';
};


const handleImageError = () => {
  userImageError.value = true;
};



</script>

<style scoped>
.menu {
  display: flex;
  gap: 20px;
  align-items: center;
}


.link {
  text-decoration: none;
  color: black;
}

.header-link {
  color: white !important;
  font-size: 16px;
  font-weight: 600;
  transition: color 0.2s ease;
}

.header-link:hover {
  color: var(--accent-blue) !important;
}

a.router-link-active {
  text-decoration-line: underline;
  -webkit-text-decoration-line: underline;
  text-decoration-color: rgb(var(--v-theme-primary));
  -webkit-text-decoration-color: rgb(var(--v-theme-primary));
  text-decoration-thickness: 3px;
  -webkit-text-decoration-thickness: 3px;
  text-underline-position: under;
  -webkit-text-underline-position: under;
}

.full-width-bar {
  max-width: 100% !important;
  width: 100% !important;
}

.full-width-bar :deep(.v-toolbar__content) {
  max-width: 100% !important;
  padding-left: 16px;
  padding-right: 16px;
}

.app-bar-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}
</style>
