# Quiz UI Integration Guide

## Overview
This document outlines the API contracts and integration flow for implementing the **Quiz Module** in the React LMS application.

**Base URL**: `/api/v1/quiz`

### Core Workflow
1.  **Generate**: User selects difficulty/topic -> Create Session.
2.  **Start**: Initialize session -> Get Question 1.
3.  **Interaction Loop**:
    - User selects option -> Click "Next" -> Save & Get Q(i+1).
    - User clicks "Previous" -> Save & Get Q(i-1).
4.  **Submit**: User finishes last question -> Click "Submit" -> Close Session.

---

## 1. Generate Quiz Session
**Purpose**: Creates a new quiz session based on user references.

- **Endpoint**: `POST /generate`
- **Request Body**:
  ```json
  {
    "user_id": "string",
    "session_id": "string",
    "grade": "9",
    "subject": "Math",
    "topic": "Algebra",        // Optional
    "subtopic": "Linear Eq",   // Optional
    "difficulty": "Intermediate",
    "num_questions": 10,
    "time_limit": 600          // Optional (seconds)
  }
  ```
- **Response** (Success 201):
  ```json
  {
    "quiz_session_id": "uuid-string",
    "num_questions": 10,
    "status": "not_started",
    ...
  }
  ```
- **UI Action**: Store `quiz_session_id` in React State/Context.

---

## 2. Start Quiz
**Purpose**: Initializes the quiz (starts timer, etc.) and fetches the first question.

- **Endpoint**: `POST /start`
- **Request Body**:
  ```json
  {
    "quiz_session_id": "uuid-string",
    "user_id": "string",
    "session_id": "string"
  }
  ```
- **Response** (Success 200): Returns **Question Object** (see structure below).
- **UI Action**: Display the returned question. Initialize `currentQuestionIndex = 0`.

---

## 3. Navigation (Next & Previous)
**Purpose**: Submits the *current* selection and navigates to the adjacent question.

### Next Question
- **Endpoint**: `POST /next_question`
- **Request Body**:
  ```json
  {
    "quiz_session_id": "uuid-string",
    "user_id": "string",
    "session_id": "string",
    "question_num": 0,           // Current Index (0-based)
    "selected_option": "A",      // Option ID (e.g., "A", "True", "A,C")
    "hints_used": 1              // Count of hints revealed
  }
  ```
- **Response**:
  - **Question Object**: If next question exists.
  - **`null`**: If the quiz is finished (user is at last question).

### Previous Question
- **Endpoint**: `POST /previous_question`
- **Request Body**: Same as `next_question` (sends current state to save before moving back).
- **Response**:
  - **Question Object**: If previous question exists.
  - **`null`**: If at start.

---

## 4. Submit Quiz
**Purpose**: Submits the final answer and marks the session as completed.

- **Endpoint**: `POST /submit`
- **Request Body**: Same as `next_question`.
  - **Note**: This should be called when the user clicks "Submit" on the **last** question.
- **Response**:
  ```json
  {
    "message": "Quiz submitted successfully.",
    "status": "completed"
  }
  ```
- **UI Action**: Redirect to Result/Summary page.

---

## Common Data Structure: Reference Question Object
All navigation endpoints (`start`, `next`, `previous`) return this standardized object.

```json
{
  // Question Details
  "question_id": "q-123",
  "question_type": "multiple_choice", // "single_select", "true_false"
  "questionText": "Solve for x...",
  "options": [
    { "id": "A", "text": "5" },
    { "id": "B", "text": "10" }
  ],
  "hint": "Check the slope...",
  "explanation": "Derived from...",

  // User State (Pre-filled if user visited matching this question before)
  "selected_option": "A",   // The option the user previously selected
  "is_correct": false,      // Internal grading status (optional to show)
  "hints_used": 0           // Number of hints they used
}
```

### UI Implementation Checklist
1.  **State Persistence**: When navigating, ALWAYS send the `selected_option` of the *current* question to the API (Next/Prev). The API saves it.
2.  **Pre-fill Selection**: When the API returns a Question Object, check `selected_option`. If not empty, pre-select that option in the UI. parameters
3.  **Completion Check**:
    - If `next_question` returns `null`, the UI should probably change the "Next" button to "Submit".
    - Or, if `currentQuestionIndex === totalQuestions - 1`, verify with user and call `/submit`.

---

## Error Handling
- **404 Not Found**: Session expired or invalid ID. Redirect to Home/Generate.
- **400 Bad Request**: Invalid `question_num` (e.g., out of bounds).
- **500 Internal Error**: Retry or show "Service unavailable".
