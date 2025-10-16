<template>
  <div class="bubble bubble-bottom-right">
    <slot></slot>
  </div>
</template>

<script setup></script>

<style scoped>
.bubble {
  position: relative;
  line-height: 1.5;
  max-width: 320px;
  width: fit-content;
  background: var(--accent-blue);
  border-radius: 12px 12px 2px 12px;
  text-align: left;
  color: var(--navy-text);
  padding: 6px 12px;
  margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: 14px;
}

.bubble-bottom-right:before {
  display: none; /* Remove decorative tail for cleaner look */
}
</style>
