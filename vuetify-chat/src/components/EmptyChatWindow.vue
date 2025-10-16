<template>
    <div class="empty-chat-container">
        <div class="empty-chat-content">
            <p class="empty-chat-text">Select a contact to start conversation</p>
        </div>
    </div>
</template>

<script setup>

</script>

<style scoped>
.empty-chat-container {
  width: 100%;
  height: calc(100vh - 64px);
  background-color: var(--section-card-background);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chat-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chat-text {
  color: var(--greyed-out-text);
  font-size: 18px;
  user-select: none;
  text-align: center;
}
</style>