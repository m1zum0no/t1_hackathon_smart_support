<template>
  <v-card class="mx-auto my-10 py-8 px-6 register-card" width="440px" elevation="3">
    <v-card-title class="text-center register-title mb-6">
      <v-icon size="large" color="primary" class="mb-2">mdi-account-plus</v-icon>
      <div>Create Account</div>
      <div class="text-subtitle-1 text-greyed-out mt-1">Join our support platform</div>
    </v-card-title>

    <form @submit.prevent="submit">
      <v-text-field 
        v-model="firstName.value.value" 
        :counter="20" 
        :error-messages="firstName.errorMessage.value"
        label="First Name" 
        variant="outlined"
        density="comfortable"
        clearable 
        class="mb-3"
        prepend-inner-icon="mdi-account"
      ></v-text-field>

      <v-text-field 
        v-model="lastName.value.value" 
        :counter="20" 
        :error-messages="lastName.errorMessage.value"
        label="Last Name" 
        variant="outlined"
        density="comfortable"
        clearable 
        class="mb-3"
        prepend-inner-icon="mdi-account"
      ></v-text-field>

      <v-text-field 
        v-model="username.value.value" 
        :counter="20" 
        :error-messages="username.errorMessage.value"
        label="Username" 
        variant="outlined"
        density="comfortable"
        clearable 
        class="mb-3"
        prepend-inner-icon="mdi-account-circle"
      ></v-text-field>

      <v-text-field 
        v-model="email.value.value" 
        :error-messages="email.errorMessage.value" 
        label="E-mail"
        variant="outlined"
        density="comfortable"
        clearable 
        class="mb-3"
        prepend-inner-icon="mdi-email"
      ></v-text-field>

      <v-text-field 
        v-model="password.value.value" 
        label="Password" 
        :error-messages="password.errorMessage.value"
        variant="outlined"
        density="comfortable"
        :type="passwordType" 
        :append-inner-icon="passwordIcon" 
        @click:append-inner="toggleShow"
        class="mb-3" 
        autocomplete="on"
        prepend-inner-icon="mdi-lock"
      ></v-text-field>

      <v-btn 
        color="primary" 
        class="register-btn" 
        size="large" 
        width="100%"
        type="submit"
        elevation="0"
      >
        Create Account
      </v-btn>

    </form>
    <div class="text-center mt-5 login-link no-select">
      Already have an account?
      <a href="/login/" class="link-accent">Sign In</a>
    </div>
    <v-alert v-if="registrationError" type="error" variant="tonal" class="mt-4">
      {{ registrationError }}
    </v-alert>
  </v-card>
</template>
<script setup>
import { ref } from "vue";
import { useField, useForm } from "vee-validate";
import { useUserStore } from "@/store/userStore";

import { useRouter } from "vue-router";


const userStore = useUserStore();
const router = useRouter();
const registrationError = ref(null);

const supportedImageFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']


// Shared validation function for firstName, lastName, and username
function validateName(value) {
  if (!value) {
    return "Field cannot be blank"
  } else if (value?.length < 2) {
    return "Field needs to be at least 2 characters.";
  } else {
    return true;
  }
}
const { handleSubmit, handleReset } = useForm({
  validationSchema: {
    firstName(value) {
      return validateName(value);
    },
    lastName(value) {
      return validateName(value);
    },
    username(value) {
      if (!value) {
        return "Field cannot be blank"
      } else if (value?.length < 2) {
        return "Field needs to be at least 2 characters";
      } else if (/\s/.test(value)) {
        return "Username cannot contain spaces";
      }
      return true;
    },
    // shorter regex alternative: /[^\s@]+@[^\s@]+\.[^\s@]+/
    email(value) {
      // fully compliant with the RFC-2822 spec for email addresses.
      if (/\s/.test(value)) {
        return "Email cannot contain spaces";
      }
      if (/(?:[a-z0-9+!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/i.test(value)) return true;
      return "Must be a valid e-mail";
    },
    password(value) {
      if (value?.length >= 6) return true;

      return "Password needs to be at least 6 characters";
    },

    profileImage(value) {
      if (value?.[0]?.size > (20 * 1024 * 1024)) {
        return "Image size should be less than 20 MBs!";
      }
      if (value && !supportedImageFormats.includes(value?.[0]?.type)) {
        return "Image format is not supported!";
      }
      return true;
    },
  },
});
const firstName = useField("firstName");
const lastName = useField("lastName");
const username = useField("username");
const email = useField("email");
const password = useField("password");
const profileImage = useField("profileImage");

const passwordIcon = ref("mdi-eye");
const showPassword = ref(false);
const passwordType = ref("password");

const toggleShow = () => {
  showPassword.value = !showPassword.value;
  if (showPassword.value) {
    passwordType.value = "text";
    passwordIcon.value = "mdi-eye-off";
  } else {
    passwordType.value = "password";
    passwordIcon.value = "mdi-eye";
  }
};

const submit = handleSubmit(async (data) => {
  let userData = {
    first_name: data.firstName,
    last_name: data.lastName,
    username: data.username,
    email: data.email,
    password: data.password,
    uploaded_image: data.profileImage?.[0]
  };

  try {
    const response = await userStore.register(userData);
    setTimeout(() => {
      router.push("/login/"), 50;
    });
  } catch (error) {
    console.error("Error", error);
    if (error.response?.data?.detail) {
      registrationError.value = error.response.data.detail;
    } else {
      registrationError.value = "An error occurred during registration.";
      handleReset();
    }
  }
});
</script>

<style scoped>
.register-card {
  background-color: var(--section-card-background);
  border-radius: 12px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.register-title {
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

.register-btn {
  background-color: var(--navy) !important;
  color: var(--navy-text) !important;
  border-radius: 8px !important;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
}

.register-btn:hover {
  background-color: var(--greyed-out-text) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
}

.login-link {
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
