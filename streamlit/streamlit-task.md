# Streamlit Chatbot Implementation Task List

## Project Overview
Build a Streamlit-based chatbot interface for the FAQ RAG system with sample question cards and API integration.

**Reference**: `chatbot-spec.md` contains the full specification and design.

---

## Phase 1: Project Setup

### Task 1.1: Create Directory Structure
- [x] Create `streamlit/components/` directory
- [x] Create `streamlit/services/` directory
- [x] Create `streamlit/utils/` directory
- [x] Create `__init__.py` files in each directory

### Task 1.2: Install Dependencies
- [x] Add `streamlit` to `requirements.txt`
- [x] Verify `requests` is in `requirements.txt`
- [ ] Run `pip install -r requirements.txt`

### Task 1.3: Environment Configuration
- [x] Add `API_URL` to `.env-sample`
- [ ] Create `.env` file with `API_URL=http://localhost:8000`

---

## Phase 2: Core Implementation

### Task 2.1: Create API Client Service
**File**: `streamlit/services/api_client.py`

- [x] Create `FAQAPIClient` class
- [x] Implement `__init__` with base_url and timeout
- [x] Implement `health_check()` method
- [x] Implement `ask(question, top_k)` method
- [x] Implement `get_ingestion_status()` method
- [x] Implement `ingest_documents()` method
- [x] Add error handling and logging
- [ ] Test API client with mock calls

### Task 2.2: Create Configuration Utility
**File**: `streamlit/utils/config.py`

- [x] Create function to load API URL from env
- [x] Create function to get default timeout
- [x] Create function to get sample questions config

### Task 2.3: Create Sidebar Component
**File**: `streamlit/components/sidebar.py`

- [x] Create `render_sidebar()` function
- [x] Add API URL input field
- [x] Add API status indicator (✅/❌)
- [x] Add ingestion status display
- [x] Add "Clear Chat History" button
- [x] Return updated settings dict

### Task 2.4: Create Sample Cards Component
**File**: `streamlit/components/sample_cards.py`

- [x] Create `render_sample_cards()` function
- [x] Define sample questions by category (from actual FAQ docs):
  - [x] **Authentication** (`faq_auth.md`):
    - "How do I reset my password?"
  - [x] **Employee** (`faq_employee.md`):
    - "What is our unlimited PTO policy?"
    - "How does our equity vesting schedule work?"
    - "How much PTO is required per year?"
    - "How do I request time off?"
    - "What is the notice period for PTO requests?"
    - "When are equity grants reviewed?"
  - [x] **SSO** (`faq_sso.md`):
    - "How do I enable SSO?"
    - "Who can enable SSO for my account?"
  - [x] **General/Technical**:
    - "Explain how the document retrieval works"
    - "How accurate are the answers?"
    - "What sources are used for generating answers?"
- [x] Implement 4-column grid layout
- [x] Add button click handlers
- [x] Add hover effects with custom CSS
- [ ] Test card rendering

### Task 2.5: Create Chat Interface Component
**File**: `streamlit/components/chat_interface.py`

- [x] Create `render_chat_messages()` function
- [x] Display user messages (right aligned)
- [x] Display assistant messages (left aligned)
- [x] Add source expander for each answer
- [x] Add loading spinner for pending responses

### Task 2.6: Create Input Area Component
**File**: `streamlit/components/input_area.py`

- [x] Create `render_input_area()` function
- [x] Implement `st.chat_input()` with placeholder
- [x] Handle empty input validation
- [x] Return user input string

---

## Phase 3: Main Application

### Task 3.1: Create Main App File
**File**: `streamlit/app.py`

- [x] Add page configuration (`st.set_page_config`)
- [x] Add custom CSS styling
- [x] Initialize session state:
  - [x] `messages` list
  - [x] `api_url` string
- [x] Render header with title and model selector
- [x] Integrate sidebar component
- [x] Integrate sample cards component
- [x] Integrate chat interface component
- [x] Integrate input area component
- [x] Wire up question selection to chat
- [x] Wire up input submission to API call
- [x] Handle API errors gracefully

### Task 3.2: Implement API Integration
- [x] Import `FAQAPIClient` from services
- [x] Create client instance with session URL
- [x] Implement question handling:
  - [x] Add user message to history
  - [x] Call `client.ask()` with question
  - [x] Display streaming response (if supported)
  - [x] Add assistant message with sources
- [x] Implement error handling:
  - [x] Connection errors
  - [x] Timeout errors
  - [x] API errors (4xx, 5xx)

### Task 3.3: Add Custom Styling
**File**: `streamlit/style.css` (optional) or inline

- [x] Sample card hover effects
- [x] Chat bubble styling
- [x] Input area shadow and rounding
- [x] Hide Streamlit branding
- [x] Responsive layout adjustments

---

## Phase 4: Testing

### Task 4.1: Unit Testing
- [ ] Test API client methods
- [ ] Test component rendering
- [ ] Test session state management

### Task 4.2: Integration Testing
- [ ] Start API server: `python api_server.py`
- [ ] Ingest test documents: `POST /ingest`
- [ ] Test sample card clicks
- [ ] Test manual question input
- [ ] Verify answer display
- [ ] Verify source display
- [ ] Test error scenarios (API down)

### Task 4.3: UI/UX Testing
- [ ] Verify responsive layout
- [ ] Test with different screen sizes
- [ ] Check loading states
- [ ] Verify chat history persistence
- [ ] Test clear history function

---

## Phase 5: Documentation & Deployment

### Task 5.1: Update README
- [ ] Add Streamlit app section
- [ ] Add screenshots
- [ ] Document running instructions

### Task 5.2: Create Launch Script
**File**: `start-streamlit.sh`

- [x] Check API server status
- [x] Set environment variables
- [x] Launch Streamlit app
- [x] Add auto-open browser option

### Task 5.3: Create Requirements Update
- [x] Update `requirements.txt` with streamlit
- [x] Add version constraints
- [ ] Test clean install

### Task 5.4: Implement DEBUG Logging (DEBUG.md)
- [x] Add logging configuration to app.py
- [x] Add [STREAMLIT] component tags
- [x] Log entry (>>>) and exit (<<<) points
- [x] Add timing/elapsed metrics
- [x] Add data previews for large content
- [x] Implement DEBUG in api_client.py
- [x] Implement DEBUG in sidebar.py
- [x] Use appropriate log levels (DEBUG, INFO, ERROR)
- [x] Add exc_info=True for exception logging

---

## File Creation Checklist

```
streamlit/
├── app.py                    [x] Create
├── style.css                 [x] Inline in app.py
├── components/
│   ├── __init__.py           [x] Create
│   ├── sidebar.py            [x] Create
│   ├── chat_interface.py     [x] Create
│   ├── sample_cards.py       [x] Create
│   └── input_area.py         [x] Create
├── services/
│   ├── __init__.py           [x] Create
│   └── api_client.py         [x] Create
└── utils/
    ├── __init__.py           [x] Create
    └── config.py             [x] Create
```

---

## Quick Start Commands

```bash
# 1. Install dependencies
pip install streamlit requests

# 2. Ensure API server is running
python api_server.py &

# 3. Ingest documents (if not already done)
curl -X POST http://localhost:8000/ingest

# 4. Run Streamlit app
cd streamlit
streamlit run app.py
```

---

## Acceptance Criteria

- [ ] App launches without errors
- [ ] Sample question cards display correctly (4 columns)
- [ ] Clicking a card sends the question to chat
- [ ] API `/ask` endpoint is called correctly
- [ ] Answers display with proper formatting
- [ ] Sources are shown in expandable section
- [ ] Manual input works correctly
- [ ] Error handling shows user-friendly messages
- [ ] Chat history persists during session
- [ ] Clear history button works
- [ ] API status indicator is accurate
- [ ] Sidebar settings are functional

---

## Priority Order

1. **P0 - Critical**: `api_client.py`, `app.py` (basic functionality)
2. **P1 - High**: `sample_cards.py`, `chat_interface.py`
3. **P2 - Medium**: `sidebar.py`, `input_area.py`, styling
4. **P3 - Low**: `config.py`, optional enhancements

---

## Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Setup | 15 min |
| Phase 2 | Core Components | 2 hours |
| Phase 3 | Main App | 1 hour |
| Phase 4 | Testing | 1 hour |
| Phase 5 | Documentation | 30 min |
| **Total** | | **~5 hours** |