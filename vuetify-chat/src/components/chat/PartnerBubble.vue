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
      :color="isSelected ? 'yellow-darken-3' : 'yellow-darken-2'"
      class="lightbulb-btn"
      title="Add to AI Query">
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
  line-height: 24px;
  max-width: 300px;
  width: fit-content;
  background: #f5f5f5;
  border-radius: 25px;
  text-align: left;
  color: #000;
  padding: 6px 12px;
  margin-bottom: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bubble:hover {
  background: #eeeeee;
}

.bubble-selected {
  background: #fff9e6 !important;
}

.bubble-bottom-left:before {
  content: "";
  width: 0px;
  height: 0px;
  position: absolute;
  border-left: 20px solid #f5f5f5;
  border-right: 10px solid transparent;
  border-top: 10px solid #f5f5f5;
  border-bottom: 15px solid transparent;
  left: 8px;
  bottom: -12px;
  transform: rotate(10deg);
  z-index: -1;
}

.bubble-selected.bubble-bottom-left:before {
  border-left-color: #fff9e6;
  border-top-color: #fff9e6;
}

.lightbulb-btn {
  opacity: 0.7;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.lightbulb-btn:hover {
  opacity: 1;
}
</style>
