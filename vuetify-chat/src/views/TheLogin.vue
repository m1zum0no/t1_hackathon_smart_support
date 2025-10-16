<template>
  <v-card class="mx-auto mt-10 py-8 px-6 login-card" width="420px" elevation="3">
    <v-card-title class="text-center login-title mb-6">
      <v-icon size="large" color="primary" class="mb-2">mdi-shield-lock</v-icon>
      <div>Knowledge Base Support</div>
      <div class="text-subtitle-1 text-greyed-out mt-1">Sign in to continue</div>
    </v-card-title>
    <form @submit.prevent="submit">
      <v-text-field 
        v-model="username.value.value" 
        :error-messages="username.errorMessage.value" 
        label="Username or Email"
        variant="outlined"
        density="comfortable"
        clearable 
        class="mb-3"
        prepend-inner-icon="mdi-account"
      ></v-text-field>

      <v-text-field 
        v-model="password.value.value" 
        label="Password" 
        :error-messages="password.errorMessage.value"
        variant="outlined"
        density="comfortable"
        :type="passwordType" 
        :append-inner-icon="passwordIcon"
        prepend-inner-icon="mdi-lock"
        @click:append-inner="toggleShow"
        class="mb-4"
      ></v-text-field>

      <v-btn 
        color="primary" 
        class="login-btn" 
        width="100%"
        size="large" 
        type="submit"
        elevation="0"
      >
        Sign In
      </v-btn>
    </form>
    <div class="text-center mt-5 register-link no-select">
      Don't have an account?
      <a href="/register/" class="link-accent">Create Account</a>
    </div>
    <v-alert v-if="loginError" type="error" variant="tonal" class="mt-4">{{ loginError }}</v-alert>
  </v-card>
</template>

<script setup>

import { ref } from "vue";
import { useField, useForm } from "vee-validate";
import { useRouter } from "vue-router";
import { useUserStore } from "@/store/userStore";
import { useTheme } from 'vuetify'
import { storeToRefs } from "pinia";
import { event } from "vue-gtag";


const userStore = useUserStore();
const router = useRouter();
const loginError = ref(null);
const theme = useTheme();


const { currentTheme } = storeToRefs(userStore);


const { handleSubmit, handleReset } = useForm({
  validationSchema: {
    username(value) {

      if (!value) {
        return "Field cannot be blank"
      } else if (value?.length < 2) {
        return "Field needs to be at least 2 characters";
      } else if (/\s/.test(value)) {
        return "Field cannot contain spaces";
      }
      return true;
    },
    password(value) {
      if (value?.length >= 6) return true;
      return "Password needs to be at least 6 characters";
    },
  },
});

const submit = handleSubmit(async (userData) => {
  try {
    handleReset();
    await userStore.login(userData);

    // set the theme
    theme.global.name.value = currentTheme.value;
    
    loginGA();

    setTimeout(() => {
      router.push("/chat/"), 50;
    });
  } catch (error) {
    console.log("ERROR", error);
    if (error.message === "Network Error") {
      loginError.value = "Network error";
    } else if (error.response?.data?.detail) {
      loginError.value = error.response.data.detail;
    } else {
      loginError.value = "An error occurred during login";
    }
  }
});

const username = useField("username");
const password = useField("password");

const passwordIcon = ref("mdi-eye");
const showPassword = ref(false);
const passwordType = ref("password");

const toggleShow = () => {
  showPassword.value = !showPassword.value;
  if (showPassword.value) {
    passwordType.value = "text";
    passwordIcon.value = "mdi-eye-off"


  } else {
    passwordType.value = "password";
    passwordIcon.value = "mdi-eye"
  }
}

const loginGA = () => {
  event("user-logged-in", {
    event_category: "analytics",
    event_label: "User Logged In",
    value: 1,
  });
}

</script>

<style scoped>
.login-card {
  background-color: var(--section-card-background);
  border-radius: 12px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.login-title {
  color: var(--navy);
  font-weight: 600;
  font-size: 1.5rem;
  letter-spacing: 0.25px;
  display: block;
}

.text-greyed-out {
  color: var(--greyed-out-text);
  font-weight: 400;
}

.login-btn {
  background-color: var(--navy) !important;
  color: var(--navy-text) !important;
  border-radius: 8px !important;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
}

.login-btn:hover {
  background-color: var(--greyed-out-text) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
}

.register-link {
  color: var(--text);
  font-size: 14px;
}

.no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.link-accent {
  color: var(--accent-blue);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.link-accent:hover {
  color: var(--navy);
  text-decoration: underline;
}

:deep(.v-field) {
  border-radius: 8px !important;
}

:deep(.v-field--focused) {
  border-color: var(--accent-blue) !important;
}
</style>