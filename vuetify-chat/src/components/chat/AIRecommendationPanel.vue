<template>
  <v-card class="ai-panel rounded-0" elevation="0">
    <v-card-title class="panel-header">
      <v-icon color="white" class="mr-2" size="small">mdi-lightbulb-on</v-icon>
      Knowledge Base Assistant
    </v-card-title>
    
    <v-divider></v-divider>
    
    <!-- User Query Section - Always visible -->
    <v-card class="query-card" elevation="0">
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
            clearable
            @click:clear="editableQuery = ''"
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
      <!-- Low confidence state - "Ответ не найден" -->
      <div v-if="isExtremelyLowConfidence" class="text-center pa-6">
        <v-icon color="grey" size="48" class="mb-3">mdi-information-outline</v-icon>
        <p class="text-grey text-h6 mb-0">Ответ не найден</p>
      </div>
      
      <!-- Normal confidence state -->
      <div v-else>
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
        
        <!-- Main recommendation -->
        <div class="hint-response mb-3">
          <div class="d-flex justify-space-between align-center mb-2">
            <strong>Instructions:</strong>
            <v-btn
              @click="copyRecommendation(currentHint.content)"
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
        
        <!-- Alternative candidates -->
        <div v-if="hasAlternatives" class="alternatives-section">
          <v-divider class="my-3"></v-divider>
          <div class="mb-2">
            <strong>Alternative Recommendations:</strong>
            <span class="text-caption text-grey ml-2">(Similar confidence)</span>
          </div>
          
          <v-expansion-panels variant="accordion" class="mb-3">
            <v-expansion-panel
              v-for="(alt, index) in sortedAlternatives"
              :key="index"
              elevation="0"
            >
              <v-expansion-panel-title class="pa-3">
                <div class="d-flex align-center gap-2 flex-wrap">
                  <v-chip size="x-small" :color="getConfidenceColor(alt.confidence)" prepend-icon="mdi-chart-line">
                    {{ getConfidencePercentage(alt.confidence) }}
                  </v-chip>
                  <v-chip v-if="alt.category" size="x-small" color="primary">
                    {{ alt.category }}
                  </v-chip>
                  <v-chip v-if="alt.subcategory" size="x-small" color="secondary">
                    {{ alt.subcategory }}
                  </v-chip>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <div class="alternative-text pa-2">
                  {{ alt.response }}
                </div>
                <div class="d-flex justify-end mt-2">
                  <v-btn
                    @click="copyRecommendation(alt.response)"
                    size="x-small"
                    variant="text"
                    color="primary"
                    prepend-icon="mdi-content-copy"
                  >
                    Copy
                  </v-btn>
                </div>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </div>
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

// Check if confidence is extremely low (below 30%)
const isExtremelyLowConfidence = computed(() => {
  if (!currentHint.value) return false;
  const confValue = typeof currentHint.value.confidence === 'number' 
    ? currentHint.value.confidence 
    : parseInt(currentHint.value.confidence) || 0;
  return confValue < 30;
});

// Check if there are alternative recommendations
const hasAlternatives = computed(() => {
  return currentHint.value?.alternatives && currentHint.value.alternatives.length > 0;
});

// Sort alternatives by confidence descending
const sortedAlternatives = computed(() => {
  if (!hasAlternatives.value) return [];
  return [...currentHint.value.alternatives].sort((a, b) => b.confidence - a.confidence);
});

const copyRecommendation = async (text) => {
  if (text) {
    try {
      await navigator.clipboard.writeText(text);
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
  background-color: var(--section-card-wrapper);
  box-shadow: none !important;
}

.panel-header {
  background: var(--navy);
  color: var(--navy-text);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 600;
  font-size: 1rem;
  padding: 16px;
  letter-spacing: 0.25px;
}

.query-card {
  background-color: var(--section-card-wrapper);
  box-shadow: none !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.query-section {
  padding: 16px !important;
}

.query-input-row {
  align-items: flex-end !important;
}

.query-textarea {
  font-size: 14px;
  flex: 1;
}

.query-textarea :deep(.v-field) {
  background-color: var(--section-card-background);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.query-textarea :deep(.v-field--focused) {
  box-shadow: 0 2px 6px rgba(74, 144, 226, 0.15);
}

.hint-content {
  overflow-y: auto;
  max-height: calc(100vh - 400px);
  padding: 16px !important;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
}

.hint-response {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
  user-select: none;
}

.recommendation-text {
  white-space: pre-wrap;
  background-color: var(--section-card-background);
  padding: 14px;
  border-radius: 8px;
  border: 1px solid var(--section-card-wrapper);
  border-left: 3px solid var(--accent-blue);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.hint-template {
  font-size: 14px;
  color: var(--greyed-out-text);
  background-color: var(--section-card-background);
  padding: 14px;
  border-radius: 8px;
  border: 1px solid var(--section-card-wrapper);
  border-left: 3px solid var(--accent-blue-light);
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

.alternatives-section {
  margin-top: 16px;
}

.alternative-text {
  white-space: pre-wrap;
  background-color: var(--section-card-background);
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid var(--section-card-wrapper);
}

/* Chip styling override */
:deep(.v-chip) {
  font-size: 12px;
  font-weight: 500;
}

/* Expansion panel styling */
:deep(.v-expansion-panel) {
  background-color: var(--section-card-background) !important;
  border: 1px solid var(--section-card-wrapper);
  border-radius: 6px !important;
  margin-bottom: 8px;
}

:deep(.v-expansion-panel-title) {
  font-size: 13px;
  color: var(--text);
}
</style>
