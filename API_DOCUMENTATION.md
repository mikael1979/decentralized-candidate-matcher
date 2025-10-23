Kyllä, voin kääntää laajennetun Markdown-dokumentaation englanniksi. Alla on käännetty versio, joka säilyttää saman rakenteen, selkeyden ja kattavuuden kuin suomenkielinen versio. Tämä dokumentaatio sopii suoraan GitHubiin (esim. `API_DOCS_EN.md`) ja tukee frontend-kehittäjiä, jotka työskentelevät englanninkielisessä ympäristössä. Käännös on tehty huolellisesti, jotta termit ja tekniset yksityiskohdat ovat tarkkoja ja luonnollisia englanniksi.

# Decentralized Candidate Matcher (DCM) API Documentation

This documentation describes the RESTful API for the Decentralized Candidate Matcher (DCM) backend, which supports managing election data, moderating questions, handling candidate profiles, and comparing parties. The API is built with Flask and uses JSON format for requests and responses. It covers both admin and public endpoints, authentication mechanisms, and error handling.

## Table of Contents
- [General Information](#general-information)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Admin: Authentication](#admin-authentication)
  - [Admin: Question Management](#admin-question-management)
  - [Admin: IPFS and Synchronization](#admin-ipfs-and-synchronization)
  - [Admin: Settings](#admin-settings)
  - [Candidate Management](#candidate-management)
  - [Party Management](#party-management)
  - [Public Endpoints](#public-endpoints)
- [Example Requests](#example-requests)
- [Swagger Documentation](#swagger-documentation)
- [Tips for Frontend Developers](#tips-for-frontend-developers)

## General Information
- **Base URL**: For development, `http://localhost:5000/api`; in production, replace with the actual URL (e.g., `https://api.dcm.example.com/api`).
- **Format**: All requests and responses are in JSON (`Content-Type: application/json`).
- **Versioning**: The current API version is 1.0.0.
- **Timestamps**: Use ISO 8601 format (e.g., `2025-10-23T17:06:00Z`).
- **Language**: Question texts support multilingualism (e.g., `{ "fi": "text", "en": "text" }`). The default is `en` (English) if not specified.
- **IPFS Integration**: Questions and data can be synchronized to IPFS, allowing the frontend to fetch data directly from an IPFS node (using CIDs).

## Authentication
Most admin endpoints require authentication. Two methods are supported:
1. **Session-based**:
   - Log in via `POST /api/admin/login` (returns a session cookie).
   - Include the cookie in requests (automatically handled by browsers, or set `Cookie: session=...`).
2. **JWT (Bearer Token)**:
   - After login, a JWT token is returned (`Authorization: Bearer <token>`).
   - Include in the header: `Authorization: Bearer eyJ...`.

**Note**: Public endpoints (e.g., `/api/questions`, `/api/candidates`) do not require authentication.

## Error Handling
All error responses follow this format:
```json
{
  "success": false,
  "error": "Descriptive error message"
}
```
Common status codes:
- `400`: Invalid request (e.g., missing parameter).
- `401`: Authentication failed.
- `404`: Resource not found (e.g., candidate ID does not exist).
- `500`: Server error (rare, check logs).

## API Endpoints

### Admin: Authentication
#### `POST /api/admin/login`
Logs in an admin user.
- **Body**:
  ```json
  {
    "password": "securepassword123"
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Login successful",
    "token": "eyJ..." // JWT, if used
  }
  ```
- **Errors**: 401 (incorrect password).

#### `POST /api/admin/logout`
Logs out, invalidating the session or token.
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Logged out"
  }
  ```

#### `GET /api/admin/status`
Checks the admin's authentication status.
- **Response** (200):
  ```json
  {
    "authenticated": true,
    "login_time": "2025-10-23T17:06:00Z"
  }
  ```

### Admin: Question Management
All endpoints require authentication.

#### `GET /api/admin/questions`
Retrieves all questions, including blocked ones.
- **Response** (200):
  ```json
  [
    {
      "question_id": "q1",
      "question": { "en": "What is your stance on climate policy?" },
      "category": "Environment",
      "tags": ["climate", "policy"],
      "scale": { "min": -5, "max": 5 },
      "elo_rating": 1500,
      "blocked": false
    },
    ...
  ]
  ```

#### `POST /api/admin/block_question`
Blocks a question.
- **Body**:
  ```json
  {
    "question_id": "q1",
    "reason": "Inappropriate content"
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Question blocked"
  }
  ```
- **Errors**: 400 (missing `question_id`), 404 (question not found).

#### `POST /api/admin/unblock_question`
Unblocks a question.
- **Body**:
  ```json
  {
    "question_id": "q1"
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Question unblocked"
  }
  ```

#### `POST /api/admin/elo_update`
Manually updates a question's Elo rating.
- **Body**:
  ```json
  {
    "question_id": "q1",
    "delta": 50,
    "user_id": "user123"
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Elo updated"
  }
  ```

#### `GET /api/admin/questions/elo_ranking`
Retrieves questions sorted by Elo rating.
- **Response** (200): Same as `/api/admin/questions`, but sorted by `elo_rating` in descending order.

#### `GET /api/admin/questions/select_for_sync`
Selects questions for IPFS synchronization.
- **Query Parameters**:
  - `strategy` (string, default: `balanced`): Synchronization strategy (e.g., `elo_priority`, `fifo`).
  - `limit` (int, default: 20): Maximum number of questions.
- **Response** (200):
  ```json
  {
    "questions": [{ ... }], // Same as /api/admin/questions
    "strategy": "balanced",
    "limit": 20
  }
  ```

### Admin: IPFS and Synchronization
#### `GET /api/admin/ipfs_sync_queue`
Retrieves the current IPFS synchronization queue status.
- **Response** (200):
  ```json
  {
    "queue": [
      { "cid": "Qm...", "status": "pending", "data": { ... } },
      ...
    ]
  }
  ```

#### `POST /api/admin/process_ipfs_sync`
Manually processes the IPFS synchronization queue.
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Sync processed"
  }
  ```

#### `POST /api/admin/fetch_ipfs_questions`
Fetches questions from IPFS (using a well-known CID).
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Questions fetched",
    "questions": [{ ... }]
  }
  ```

### Admin: Settings
#### `GET /api/admin/settings`
Retrieves system settings.
- **Response** (200):
  ```json
  {
    "election": { "name": "Municipal Election 2025", "date": "2025-06-01" },
    "community_moderation": { "enabled": true, "threshold": 0.7 },
    "system": { "ipfs_enabled": true, "log_level": "DEBUG" }
  }
  ```

#### `POST /api/admin/settings`
Updates system settings.
- **Body**:
  ```json
  {
    "election": { "name": "Updated Election", "date": "2025-06-01" },
    "community_moderation": { "enabled": true },
    "system": { "ipfs_enabled": true }
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Settings updated"
  }
  ```
- **Errors**: 400 (invalid JSON or values).

### Candidate Management
#### `GET /api/candidate/<candidate_id>/profile`
Retrieves a candidate's profile.
- **Example**: `/api/candidate/c1/profile`
- **Response** (200):
  ```json
  {
    "candidate": {
      "candidate_id": "c1",
      "name": "John Doe",
      "district": "Helsinki",
      "party": "Green Party",
      "answers": [
        { "question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy" }
      ],
      "deleted": false
    }
  }
  ```
- **Errors**: 404 (candidate not found).

#### `PUT /api/candidate/<candidate_id>/answers`
Updates a candidate's answers (admin only).
- **Body**:
  ```json
  {
    "answers": [
      { "question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy" }
    ]
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Answers updated"
  }
  ```
- **Validation**: `answer` (-5 to 5), `confidence` (0 to 1).

#### `PUT /api/candidate/<candidate_id>/profile`
Updates a candidate's profile (admin only).
- **Body**:
  ```json
  {
    "name": "John Doe",
    "district": "Helsinki"
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Profile updated"
  }
  ```

### Party Management
#### `GET /api/party/<party_name>/candidates`
Retrieves all candidates for a party.
- **Example**: `/api/party/Green%20Party/candidates`
- **Response** (200):
  ```json
  {
    "candidates": [{ ... }], // Same as /api/candidate/<id>/profile
    "count": 10
  }
  ```

#### `POST /api/party/<party_name>/candidates`
Adds a candidate to a party (admin only).
- **Body**:
  ```json
  {
    "name": "John Doe",
    "district": "Helsinki",
    "answers": [{ "question_id": "q1", "answer": 3, "confidence": 0.8 }]
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "candidate_id": "c1"
  }
  ```

#### `PUT /api/party/<party_name>/candidate/<candidate_id>`
Updates a candidate's details in a party (admin only).
- **Body**: Same as `POST /api/party/<party_name>/candidates`.
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Candidate updated"
  }
  ```

#### `DELETE /api/party/<party_name>/candidate/<candidate_id>`
Soft deletes a candidate from a party (admin only).
- **Response** (200):
  ```json
  {
    "success": true,
    "message": "Candidate deleted"
  }
  ```
- **Errors**: 404 (candidate not found).

### Public Endpoints
#### `GET /api/meta`
Retrieves system metadata.
- **Response** (200):
  ```json
  {
    "system_name": "DCM",
    "version": "1.0.0",
    "description": "Decentralized Candidate Matcher"
  }
  ```

#### `GET /api/system_info`
Retrieves system information and statistics.
- **Response** (200):
  ```json
  {
    "system_name": "DCM",
    "version": "1.0.0",
    "election": { "name": "Municipal Election 2025", "date": "2025-06-01" },
    "stats": { "question_count": 100, "candidate_count": 500 }
  }
  ```

#### `GET /api/questions`
Retrieves all public (non-blocked) questions.
- **Response** (200): Same as `/api/admin/questions`, but excludes `blocked: true`.

#### `GET /api/candidates`
Retrieves all active candidates.
- **Response** (200):
  ```json
  [
    { "candidate_id": "c1", "name": "John Doe", ... },
    ...
  ]
  ```

#### `GET /api/parties`
Retrieves all party names.
- **Response** (200):
  ```json
  ["Green Party", "Blue Party", ...]
  ```

#### `GET /api/party/<party_name>`
Retrieves a party's profile and consensus answers.
- **Response** (200):
  ```json
  {
    "profile": { "description": "Eco-friendly policies" },
    "consensus": { "q1": 4, "q2": -2 }
  }
  ```

#### `POST /api/submit_question`
Submits a new question (public, subject to moderation).
- **Body**:
  ```json
  {
    "question": { "en": "What is your stance on climate policy?" },
    "category": "Environment",
    "tags": ["climate", "policy"],
    "scale": { "min": -5, "max": 5 }
  }
  ```
- **Response** (200):
  ```json
  {
    "success": true,
    "cid": "Qm..."
  }
  ```

#### `GET /api/search_questions`
Searches questions by keyword.
- **Query**: `q=climate`
- **Response** (200):
  ```json
  {
    "results": [{ ... }] // Same as /api/questions
  }
  ```

#### `GET /api/available_tags`
Retrieves all tags and their counts.
- **Response** (200):
  ```json
  {
    "tags": { "climate": 10, "policy": 15 }
  }
  ```

#### `POST /api/compare_parties`
Compares user answers to a specific party.
- **Body**:
  ```json
  {
    "user_answers": { "q1": 3, "q2": -1 },
    "party_name": "Green Party"
  }
  ```
- **Response** (200):
  ```json
  {
    "match_percentage": 85.5,
    "candidate_count": 10
  }
  ```

#### `POST /api/compare_all_parties`
Compares user answers to all parties.
- **Body**:
  ```json
  {
    "user_answers": { "q1": 3, "q2": -1 }
  }
  ```
- **Response** (200):
  ```json
  [
    { "party": "Green Party", "match_percentage": 85.5 },
    { "party": "Blue Party", "match_percentage": 60.2 },
    ...
  ]
  ```

## Example Requests
### Login (cURL)
```bash
curl -X POST http://localhost:5000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"password": "securepassword123"}'
```

### Fetch Questions (JavaScript/Fetch)
```javascript
fetch('http://localhost:5000/api/questions', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### Update Candidate Answers (admin)
```bash
curl -X PUT http://localhost:5000/api/candidate/c1/answers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"answers": [{"question_id": "q1", "answer": 3, "confidence": 0.8, "justification": "Support renewable energy"}]}'
```

### Compare Parties (JavaScript)
```javascript
fetch('http://localhost:5000/api/compare_all_parties', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_answers: { q1: 3, q2: -1 } })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

## Swagger Documentation
Detailed technical documentation and interactive testing are available via Swagger UI:
- **URL**: `/api/docs` (if integrated into Flask).
- **YAML File**: See `openapi.yaml` in the project root or paste it into [Swagger Editor](https://editor.swagger.io).
- **Usage**: Swagger UI allows testing endpoints directly in the browser, including authenticated requests (enter JWT or use session).

## Tips for Frontend Developers
1. **Displaying Questions**:
   - Use `GET /api/questions` to fetch active questions.
   - Render `question.en` (or another language) and `scale` (e.g., a slider from -5 to 5).
   - Show `tags` as filters and `category` for grouping.

2. **User Comparison**:
   - Store user answers locally (e.g., `{ q1: 3, q2: -1 }`).
   - Use `POST /api/compare_all_parties` to display party matches (sort by `match_percentage` descending).
   - Show `candidate_count` for context.

3. **IPFS Integration**:
   - To fetch data directly from IPFS, use `GET /api/admin/fetch_ipfs_questions` (admin) or integrate the IPFS-js library in the frontend using CIDs.
   - Ensure IPFS nodes are accessible (e.g., `ipfs.io` or a custom node).

4. **Authentication**:
   - Store JWT in localStorage or use session cookies in the browser.
   - Check `GET /api/admin/status` before admin operations.

5. **Error Handling**:
   - Display the `error` field message to users if `success: false`.
   - Redirect to login on 401 responses.

6. **Optimization**:
   - Cache `GET /api/questions` and `GET /api/candidates` (data changes infrequently).
   - Use pagination for large datasets (e.g., `GET /api/questions?offset=0&limit=50`, if supported).

7. **UI/UX**:
   - Use `GET /api/available_tags` for dynamic filtering.
   - Highlight high `elo_rating` questions as "popular" or emphasize them.

If you need additional examples (e.g., React code for endpoint usage), clarifications on specific endpoints, or assistance with Swagger integration, let me know! I can also generate test data or help write unit tests.
