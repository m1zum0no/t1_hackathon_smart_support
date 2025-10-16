<template>
  <router-view />
</template>

<script setup>
  //
</script>

<style>
/* Professional Banking Theme - Global Styles */
:root {
  --navy: #1e2633;
  --navy-text: #ffffff;
  --background: #ebecf5;
  --section-card-wrapper: #f4f4f9;
  --section-card-background: #ffffff;
  --text: rgb(33, 33, 33);
  --greyed-out-text: #516077;
  --accent-blue: #4a90e2;
  --accent-blue-light: #7c9cbf;
  --hover-bg: #e8e9f0;
}

/* Professional Typography */
* {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background-color: var(--background);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
}

/* Profile Image - Consistent Styling */
.profile-image {
  border-radius: 50%;
  float: left;
  width: 40px;
  height: 40px;
  object-fit: cover;
  border: 2px solid var(--section-card-wrapper);
}

/* Card Elevation Override - Subtle Shadows */
.v-card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
}

.v-card.elevation-2 {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Button Styling - Professional */
.v-btn {
  text-transform: none !important;
  font-weight: 500;
  letter-spacing: 0.25px;
}

/* Input Fields - Clean Look */
.v-field {
  border-radius: 8px !important;
}

/* Scrollbar Styling - Minimal */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--background);
}

::-webkit-scrollbar-thumb {
  background: var(--greyed-out-text);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--navy);
}
</style>