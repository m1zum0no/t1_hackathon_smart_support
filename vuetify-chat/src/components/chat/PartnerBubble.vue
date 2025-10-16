<template>
  <div ref="messageBubble" class="bubble-container">
    <div 
      class="bubble bubble-bottom-left pa-0" 
      :class="{ 'bubble-selected': isSelected }"
      @click="handleBubbleClick">
      <slot></slot>
    </div>
    <v-btn 
      @click.stop="handleLightbulbClick" 
      icon="mdi-lightbulb-on-outline" 
      variant="text" 
      size="small"
      :color="isSelected ? 'accent' : 'grey'"
      class="lightbulb-btn"
      title="Add to Knowledge Base Query">
    </v-btn>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useObserverStore } from "@/store/observerStore";
import { useMessageStore } from "@/store/messageStore";

const props = defineProps({
  messageContent: String,
  messageGuid: String
});

const observerStore = useObserverStore();
const messageStore = useMessageStore();
const messageBubble = ref(null);

const isSelected = computed(() => {
  return messageStore.isMessageSelected(props.messageGuid);
});

const handleBubbleClick = () => {
  messageStore.toggleMessageSelection(props.messageGuid, props.messageContent);
};

const handleLightbulbClick = () => {
  console.log('Lightbulb clicked for message:', props.messageContent);
  messageStore.toggleMessageSelection(props.messageGuid, props.messageContent);
};

onMounted(() => {
  if (observerStore.observer) {
    observerStore.observer.observe(messageBubble.value);
  } else {
    console.log("Could not observe, must fix");
  }
});
</script>

<style scoped>
.bubble-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.bubble {
  position: relative;
  line-height: 1.5;
  max-width: 320px;
  width: fit-content;
  background: var(--section-card-background);
  border-radius: 12px 12px 12px 2px;
  text-align: left;
  color: var(--text);
  padding: 6px 12px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--section-card-wrapper);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  font-size: 14px;
}

.bubble:hover {
  background: var(--hover-bg);
  border-color: var(--accent-blue-light);
}

.bubble-selected {
  background: #e3f2fd !important;
  border-color: var(--section-card-wrapper) !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.bubble-bottom-left:before {
  display: none; /* Remove decorative tail for cleaner look */
}

.lightbulb-btn {
  opacity: 0.6;
  transition: all 0.2s;
  flex-shrink: 0;
}

.lightbulb-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}
</style>
