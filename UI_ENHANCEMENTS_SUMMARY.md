# UI Enhancements Summary - AI Recommendation Panel

## Overview

Enhanced the AI Recommendation Panel with improved UX for displaying multiple candidates and handling low-confidence results.

---

## Changes Implemented

### 1. ✅ Removed "Source Template" Block

**Before**: Displayed a separate "Source Template" section showing the raw template text.

**After**: Template block completely removed from the UI for cleaner presentation.

**Files Changed**:
- `vuetify-chat/src/components/chat/AIRecommendationPanel.vue` (lines 112-117 removed)

---

### 2. ✅ Multiple Candidates Display

**Feature**: When multiple candidates have similar confidence scores, display up to 3 best matches sorted by confidence (descending).

**Logic**:
- **L2 (Semantic Search)**: Shows alternatives if confidence ≥ 80% and within 5% of top candidate
- **L3 (LLM Rerank)**: Shows alternatives if confidence ≥ 50% (max 2 alternatives)
- Alternatives displayed in collapsible expansion panels
- Each alternative shows: confidence, category, subcategory, and full response
- Individual copy button for each alternative

**Backend Changes** (`fastapi-chat/src/chat/rag.py`):

```python
class Candidate(BaseModel):
    """Single candidate result."""
    response: str
    confidence: int  # 0-100
    category: str = ""
    subcategory: str = ""

class Hint(BaseModel):
    # ... existing fields ...
    alternatives: list[Candidate] = []  # Multiple candidates for similar confidence
```

**L2 Alternative Logic**:
```python
# Check for similar confidence candidates (within 5% of top)
alternatives = []
for i, cand in enumerate(candidates[1:4], 1):  # Check next 3 candidates
    cand_similarity = cand.get('similarity', 0)
    cand_confidence = int(cand_similarity * 100)
    # Include if within 5% of top confidence and above 80%
    if cand_confidence >= 80 and abs(confidence_score - cand_confidence) <= 5:
        alternatives.append(Candidate(
            response=cand['template'],
            confidence=cand_confidence,
            category=cand.get('category', ''),
            subcategory=cand.get('subcategory', '')
        ))
```

**L3 Alternative Logic**:
```python
# For L3, include other top candidates if confidence is moderate
alternatives = []
if confidence_score >= 50:  # Only show alternatives if not extremely low
    for cand in top_candidates:
        if cand != selected_candidate:
            cand_similarity = cand.get('similarity', 0)
            cand_confidence = int(cand_similarity * 100)
            if cand_confidence >= 50:  # Only include decent candidates
                alternatives.append(Candidate(
                    response=cand['template'],
                    confidence=cand_confidence,
                    category=cand.get('category', ''),
                    subcategory=cand.get('subcategory', '')
                ))

alternatives=alternatives[:2]  # Max 2 alternatives (total 3 with main)
```

**Frontend Display** (`vuetify-chat/src/components/chat/AIRecommendationPanel.vue`):

```vue
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
          <v-chip size="x-small" :color="getConfidenceColor(alt.confidence)">
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
```

---

### 3. ✅ Extremely Low Confidence Handling

**Feature**: When confidence is extremely low (< 30%), show a clean "Ответ не найден" message with an information icon.

**Behavior**:
- **Hide**: Category chips, subcategory chips, copy button, recommendation text
- **Show**: Only a centered information icon and "Ответ не найден" message in grey

**Frontend Implementation**:

```vue
<!-- Low confidence state - "Ответ не найден" -->
<div v-if="isExtremelyLowConfidence" class="text-center pa-6">
  <v-icon color="grey" size="48" class="mb-3">mdi-information-outline</v-icon>
  <p class="text-grey text-h6 mb-0">Ответ не найден</p>
</div>

<!-- Normal confidence state -->
<div v-else>
  <!-- All normal UI elements -->
</div>
```

**Computed Property**:
```javascript
const isExtremelyLowConfidence = computed(() => {
  if (!currentHint.value) return false;
  const confValue = typeof currentHint.value.confidence === 'number' 
    ? currentHint.value.confidence 
    : parseInt(currentHint.value.confidence) || 0;
  return confValue < 30;
});
```

---

## UI States

### State 1: High Confidence (≥ 80%) - Single Result

**Display**:
```
[📁 Карты] [📂 Оформление]
[📊 97%] [🛣️ L2 Семантический поиск] [🕐 150ms]

Recommendation:                                    [Copy]
┌─────────────────────────────────────────────────┐
│ Для оформления карты вам необходимо...         │
└─────────────────────────────────────────────────┘
```

### State 2: High Confidence (≥ 80%) - Multiple Similar Candidates

**Display**:
```
[📁 Карты] [📂 Оформление]
[📊 95%] [🛣️ L2 Семантический поиск] [🕐 150ms]

Recommendation:                                    [Copy]
┌─────────────────────────────────────────────────┐
│ Для оформления карты вам необходимо...         │
└─────────────────────────────────────────────────┘

────────────────────────────────────────────────────

Alternative Recommendations: (Similar confidence)

▼ [📊 93%] [📁 Карты] [📂 Регистрация]
  ┌───────────────────────────────────────────────┐
  │ Вы можете оформить карту онлайн через...     │
  └───────────────────────────────────────────────┘
                                            [Copy]

▼ [📊 91%] [📁 Карты] [📂 Условия]
  ┌───────────────────────────────────────────────┐
  │ Карта MORE предоставляет следующие условия... │
  └───────────────────────────────────────────────┘
                                            [Copy]
```

### State 3: Medium Confidence (50-79%)

**Display**:
```
[📁 Карты] [📂 Оформление]
[📊 65%] [🛣️ L3 LLM rerank] [🕐 2500ms]

Recommendation:                                    [Copy]
┌─────────────────────────────────────────────────┐
│ Для оформления карты вам необходимо...         │
└─────────────────────────────────────────────────┘

────────────────────────────────────────────────────

Alternative Recommendations: (Similar confidence)

▼ [📊 62%] [📁 Карты] [📂 Регистрация]
  ...
```

### State 4: Extremely Low Confidence (< 30%)

**Display**:
```
        ⓘ
        
  Ответ не найден
```

**No chips, no buttons, just the message.**

---

## Example Scenarios

### Scenario 1: Exact Match (L1)

**Query**: "Как стать клиентом банка онлайн?"

**Response**:
- Confidence: 100%
- Alternatives: None (exact match)
- Display: Single recommendation with full metadata

### Scenario 2: High Similarity with Close Alternatives (L2)

**Query**: "Как оформить карту more?"

**Response**:
- Main: 95% confidence
- Alternative 1: 93% confidence (different subcategory)
- Alternative 2: 91% confidence (different approach)
- Display: Main recommendation + 2 collapsible alternatives

### Scenario 3: LLM Rerank with Moderate Confidence (L3)

**Query**: "Хочу получить кредит"

**Response**:
- Main: 70% confidence
- Alternative 1: 65% confidence
- Alternative 2: 62% confidence
- Display: Main recommendation + 2 collapsible alternatives

### Scenario 4: No Good Match

**Query**: "What is the weather today?"

**Response**:
- Confidence: 0%
- Display: "Ответ не найден" with info icon only

---

## Technical Details

### Backend Models

```python
class Candidate(BaseModel):
    """Single candidate result."""
    response: str
    confidence: int  # 0-100
    category: str = ""
    subcategory: str = ""

class Hint(BaseModel):
    response: str
    confidence: int  # 0-100
    category: str = ""
    subcategory: str = ""
    template: str = ""
    route: str = ""
    processing_time_ms: int = 0
    candidates_found: int = 0
    alternatives: list[Candidate] = []
```

### Frontend Computed Properties

```javascript
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
```

---

## Files Modified

### Backend
1. **`fastapi-chat/src/chat/rag.py`**
   - Added `Candidate` model
   - Updated `Hint` model with `alternatives` field
   - Modified L2 logic to detect similar confidence candidates
   - Modified L3 logic to include alternative candidates
   - Lines changed: ~50 lines

### Frontend
1. **`vuetify-chat/src/components/chat/AIRecommendationPanel.vue`**
   - Removed "Source Template" block
   - Added low confidence state UI
   - Added alternatives display with expansion panels
   - Updated `copyRecommendation` to accept text parameter
   - Added computed properties for alternatives
   - Added CSS for alternative text styling
   - Lines changed: ~100 lines

---

## Testing Checklist

- [x] High confidence single result displays correctly
- [x] Multiple alternatives show when confidence is similar
- [x] Alternatives are sorted by confidence descending
- [x] Maximum 3 total recommendations (1 main + 2 alternatives)
- [x] Low confidence (< 30%) shows "Ответ не найден" only
- [x] Category/subcategory chips hidden for low confidence
- [x] Copy button hidden for low confidence
- [x] Copy button works for each alternative
- [x] Expansion panels work correctly
- [x] "Source Template" block removed
- [x] Backend returns alternatives in response
- [x] Frontend handles missing alternatives gracefully

---

## Benefits

1. **Better UX for Ambiguous Queries**: Users can see multiple valid answers when the system isn't 100% certain
2. **Cleaner Low Confidence State**: Clear "not found" message instead of confusing low-quality results
3. **Reduced Clutter**: Removed unnecessary "Source Template" section
4. **Improved Discoverability**: Alternatives are easily accessible via expansion panels
5. **Confidence-Based Display**: UI adapts based on confidence level

---

## Future Enhancements

- Add user feedback mechanism (thumbs up/down) for each alternative
- Track which alternatives users select to improve ranking
- Add "Show more" button if there are more than 3 candidates
- Implement A/B testing for confidence thresholds
- Add tooltips explaining why alternatives are shown

---

## Summary

✅ **Source template removed** - Cleaner UI  
✅ **Multiple candidates** - Up to 3 best matches when confidence is similar  
✅ **Sorted by confidence** - Descending order  
✅ **Low confidence handling** - "Ответ не найден" with info icon  
✅ **Smart display logic** - Adapts based on confidence level  
✅ **Individual copy buttons** - For each alternative  
✅ **Expansion panels** - Collapsible alternatives for better UX  

The AI Recommendation Panel now provides a much better user experience with intelligent handling of multiple candidates and low-confidence scenarios! 🎉
