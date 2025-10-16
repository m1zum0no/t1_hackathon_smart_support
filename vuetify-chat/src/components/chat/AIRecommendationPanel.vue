<template>
  <v-card class="ai-panel rounded-0 rounded-e-lg" elevation="2">
    <v-card-title class="panel-header">
      <v-icon color="yellow-darken-2" class="mr-2">mdi-lightbulb-on</v-icon>
      AI Recommendation
    </v-card-title>
    
    <v-divider></v-divider>
    
    <!-- User Query Section - Always visible -->
    <v-card class="query-card">
      <v-card-text class="query-section pa-3">
        <div class="mb-2">
          <v-chip size="small" color="blue-grey-lighten-4" class="mb-2">
            <v-icon start size="small">mdi-message-text</v-icon>
            User Query
          </v-chip>
          <v-chip v-if="selectedMessages.length > 0" size="small" color="primary" class="ml-2">
            {{ selectedMessages.length }} message{{ selectedMessages.length !== 1 ? 's' : '' }} selected
          </v-chip>
        </div>
        <v-row align="end" justify="center" no-gutters class="query-input-row">
          <v-textarea
            v-model="editableQuery"
            placeholder="Select messages or type your query here..."
            variant="solo"
            rows="1"
            auto-grow
            max-rows="6"
            hide-details
            class="query-textarea"
          ></v-textarea>
          <v-btn
            @click="requestRecommendation"
            :disabled="!editableQuery.trim() || loading"
            :loading="loading"
            icon="mdi-lightbulb-on"
            variant="plain"
            color="primary"
            size="large"
            class="ml-1"
          >
          </v-btn>
        </v-row>
        <div class="mt-2 d-flex justify-end">
          <v-btn
            v-if="selectedMessages.length > 0"
            @click="clearSelection"
            variant="text"
            size="x-small"
            color="grey"
            prepend-icon="mdi-close-circle"
          >
            Clear Selection
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
    
    <v-divider v-if="currentHint || loading"></v-divider>
    
    <!-- Recommendation Result Section -->
    <v-card-text v-if="loading" class="hint-content">
      <div class="text-center pa-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <p class="text-grey mt-4">Getting AI recommendation...</p>
      </div>
    </v-card-text>
    
    <v-card-text v-else-if="currentHint" class="hint-content">
      <!-- Metadata chips -->
      <div class="mb-3">
        <div class="d-flex flex-wrap gap-2 mb-2">
          <v-chip v-if="currentHint.category" size="small" color="primary" prepend-icon="mdi-folder">
            {{ currentHint.category }}
          </v-chip>
          <v-chip v-if="currentHint.subcategory" size="small" color="secondary" prepend-icon="mdi-folder-outline">
            {{ currentHint.subcategory }}
          </v-chip>
          <v-chip :color="getConfidenceColor(currentHint.confidence)" size="small" prepend-icon="mdi-chart-line">
            {{ getConfidencePercentage(currentHint.confidence) }}
          </v-chip>
          <v-chip v-if="currentHint.route" size="small" color="info" prepend-icon="mdi-routes">
            {{ currentHint.route }}
          </v-chip>
          <v-chip v-if="currentHint.processing_time_ms" size="small" color="grey-darken-1" prepend-icon="mdi-clock-outline">
            {{ currentHint.processing_time_ms }}ms
          </v-chip>
        </div>
      </div>
      
      <div class="hint-response mb-3">
        <div class="d-flex justify-space-between align-center mb-2">
          <strong>Recommendation:</strong>
          <v-btn
            @click="copyRecommendation"
            size="small"
            variant="text"
            color="primary"
            prepend-icon="mdi-content-copy"
          >
            Copy
          </v-btn>
        </div>
        <div v-if="currentHint.content" class="recommendation-text">{{ currentHint.content }}</div>
        <div v-else class="recommendation-text text-grey">
          <v-icon color="warning" class="mr-2">mdi-alert</v-icon>
          No recommendation available. The system may need initialization.
        </div>
      </div>
      
      <v-divider v-if="currentHint.template" class="my-3"></v-divider>
      
      <div v-if="currentHint.template" class="hint-template">
        <strong>Source Template:</strong>
        <p class="mt-2">{{ currentHint.template }}</p>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useMessageStore } from '@/store/messageStore';

const messageStore = useMessageStore();
const { currentHint, hintLoading, selectedMessages, userQuery } = storeToRefs(messageStore);

const loading = computed(() => hintLoading.value);

// Create a local editable copy of userQuery
const editableQuery = computed({
  get: () => userQuery.value,
  set: (value) => {
    messageStore.userQuery = value;
  }
});

const requestRecommendation = async () => {
  if (editableQuery.value.trim()) {
    await messageStore.getHintForQuery(editableQuery.value);
  }
};

const clearSelection = () => {
  messageStore.clearSelectedMessages();
};

const copyRecommendation = async () => {
  if (currentHint.value && currentHint.value.content) {
    try {
      await navigator.clipboard.writeText(currentHint.value.content);
      messageStore.displaySystemMessage("success", "Recommendation copied to clipboard!", 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      messageStore.displaySystemMessage("error", "Failed to copy to clipboard", 3000);
    }
  }
};

const getConfidenceColor = (confidence) => {
  // confidence is now a number 0-100
  const confValue = typeof confidence === 'number' ? confidence : parseInt(confidence) || 0;
  if (confValue >= 80) return 'success';
  if (confValue >= 50) return 'warning';
  return 'error';
};

const getConfidencePercentage = (confidence) => {
  // confidence is now a number 0-100, just add % sign
  const confValue = typeof confidence === 'number' ? confidence : parseInt(confidence) || 0;
  return `${confValue}%`;
};
</script>

<style scoped>
.ai-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fafafa;
}

.panel-header {
  background: linear-gradient(135deg, #fffbea 0%, #fff9e6 100%);
  border-bottom: 3px solid #f9a825;
  font-weight: 600;
  font-size: 1.1rem;
  padding: 12px 16px;
}

.query-card {
  background-color: #ffffff;
  box-shadow: none !important;
}

.query-section {
  padding: 12px !important;
}

.query-input-row {
  align-items: flex-end !important;
}

.query-textarea {
  font-size: 0.9rem;
  flex: 1;
}

.hint-content {
  overflow-y: auto;
  max-height: calc(100vh - 400px);
  padding: 12px 16px !important;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
}

.hint-response {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #333;
}

.recommendation-text {
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #2196F3;
}

.hint-template {
  font-size: 0.9rem;
  color: #666;
  background-color: rgba(0, 0, 0, 0.03);
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid #9c27b0;
}

.hint-template p {
  white-space: pre-wrap;
}

.hint-confidence {
  display: flex;
  justify-content: flex-end;
}

.gap-2 {
  gap: 8px;
}
</style>
