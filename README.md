# Luna Take Home Technical Interview - Full Stack Solution

A complete full-stack iOS and backend application for social venue discovery and automated reservation booking.

**Submission by:** Roman
**Track:** Full Stack (Track 1 + Track 2 + Track 3)
**Timeline:** November 20-23, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Track Implementation](#track-implementation)
4. [Technology Stack](#technology-stack)
5. [Setup Instructions](#setup-instructions)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [API Documentation](#api-documentation)
9. [Design Decisions](#design-decisions)
10. [Use of Coding Agents](#use-of-coding-agents)

---

## Overview

This project implements a social venue discovery platform that helps users find places to visit and connects them with friends who share similar interests. The application includes AI-powered recommendations and automated reservation agents.

### Key Features

- **Personalized venue recommendations** based on location, social connections, and preferences
- **Social discovery** showing which friends are interested in each venue
- **Automated reservation system** that creates bookings when all parties confirm
- **Real-time compatibility scoring** for people recommendations
- **Intuitive SwiftUI interface** following MVVM architecture

---

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   iOS App       │
│   (SwiftUI)     │
└────────┬────────┘
         │ HTTP/JSON
         │
┌────────▼────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
┌────────▼────────┐
│  PostgreSQL     │
│   Database      │
└─────────────────┘
```

### Backend Architecture

**Pattern:** Layered Architecture with Service Layer

```
┌─────────────────────────────────────┐
│         FastAPI Routers             │
│  (users, venues, interests,         │
│   recommendations, reservations)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Service Layer               │
│  - recommendation.py                │
│  - agent.py                         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      SQLAlchemy ORM Models          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         PostgreSQL                  │
└─────────────────────────────────────┘
```

### iOS Architecture

**Pattern:** MVVM (Model-View-ViewModel)

```
┌─────────────────────────────────────┐
│            Views                    │
│  (SwiftUI declarative UI)           │
└──────────────┬──────────────────────┘
               │ Binding
┌──────────────▼──────────────────────┐
│         ViewModels                  │
│  (@Published properties,            │
│   business logic)                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         APIClient                   │
│  (URLSession, async/await)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           Models                    │
│  (Codable structs)                  │
└─────────────────────────────────────┘
```

---

## Track Implementation

### ✅ Track 1: iOS Frontend (SwiftUI)

**Architecture:** MVVM pattern as required

**Implemented Features:**

1. **User Interface Components:**
   - User selection screen for testing different user perspectives
   - Main recommendations view with venue cards
   - Venue detail view with recommended people
   - My Plans (reservations) view
   - Profile view

2. **Social Features:**
   - Display friends interested in each venue with avatars
   - Compatibility scores for recommended people
   - Visual indication of reservation status (pending/confirmed)

3. **User Flows:**
   - Browse personalized venue recommendations
   - View venue details with friend recommendations
   - Confirm interest in venues
   - View and accept reservation invitations

4. **Product-Market Fit Considerations:**
   - **Intuitive Usability:** Simple tab-based navigation, clear visual hierarchy
   - **Social Growth:** Friend avatars prominently displayed, compatibility scores encourage social connections
   - **Utility:** Personalized recommendations based on location and social graph

**Design Decisions:**
- Clean, minimal design using system fonts and SF Symbols
- Single accent color (blue) for consistency
- Card-based layout for venue recommendations
- Pull-to-refresh for real-time updates

### ✅ Track 2: Backend (Recommendation Engine + AI Agents)

**Implemented Features:**

1. **Recommendation Engine (`services/recommendation.py`):**

   **Spatial Analysis:**
   - Haversine distance calculation for accurate location-based scoring
   - Exponential decay function: closer venues score up to 50 points
   - Distance ranges: 0-1km (50pts), 1-5km (30-10pts), 5-10km (5-1pts)

   **Social Compatibility:**
   - Friendship strength scoring (0-50 points based on relationship strength)
   - Shared interest analysis (3 points per common venue)
   - Venue-specific interest bonus (+20 points if friend is interested in same venue)

   **Data Sources Considered:**
   - User's previous expressed interests in venues
   - Friend network and friendship strength values
   - Real-time location data (optional lat/lon parameters)
   - Venue popularity among friend circle

   **Algorithm:**
   ```python
   venue_score = distance_score + prior_interest_score + friend_popularity_score
   person_score = friendship_strength + shared_interests + venue_interest_bonus
   ```

2. **AI Agent System (`services/agent.py`):**

   **Auto-Reservation Agent:**
   - Monitors user interest confirmations
   - Automatically creates reservations when all participants confirm
   - Handles time window detection (prevents duplicate reservations within 30 minutes)
   - Updates reservation status to CONFIRMED when conditions met

   **Features:**
   - Participant status tracking (INVITED → ACCEPTED → CONFIRMED)
   - Automatic status promotion when all participants accept
   - Prevents duplicate reservations for same venue/time
   - Returns detailed success/failure messages

### ✅ Track 3: Full Stack Integration

**End-to-End Flows:**

1. **Recommendation Flow:**
   ```
   User opens app → iOS fetches recommendations from API
   → Backend runs recommendation engine with user's location
   → Scores venues based on proximity + social signals
   → Returns ranked venues with recommended friends
   → iOS displays in card format
   ```

2. **Interest Confirmation Flow:**
   ```
   User taps "Confirm Going" on venue
   → iOS calls POST /users/{id}/interests with CONFIRMED status
   → Backend updates UserInterest in database
   → (Future: triggers agent to check if reservation ready)
   → iOS shows confirmation message
   ```

3. **Reservation Flow:**
   ```
   Multiple users confirm interest in same venue
   → Agent detects all confirmations
   → Auto-creates Reservation with CONFIRMED status
   → Creates ReservationParticipant entries for all users
   → Users see reservation in "My Plans" tab
   ```

**Integration Quality:**
- All API endpoints return real data from PostgreSQL (no mocks)
- Proper error handling with user-friendly messages
- iOS uses async/await for clean asynchronous code
- Real-time updates via pull-to-refresh

---

## Technology Stack

### Backend
- **Python 3.11** - Modern, type-safe Python
- **FastAPI 0.115** - High-performance async web framework
- **PostgreSQL 16** - Robust relational database
- **SQLAlchemy 2.0** - ORM with modern async support
- **Pydantic 2.9** - Data validation and settings
- **Pytest** - Testing framework

### Frontend
- **SwiftUI** - Declarative UI framework
- **iOS 16+** - Target platform
- **Swift 5** - Modern, safe programming language
- **Async/Await** - Built-in concurrency
- **URLSession** - Native networking

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration
- **Google Cloud Run** - Deployment target (design)

---

## Setup Instructions

### Prerequisites

- **Backend:**
  - Docker and Docker Compose installed
  - Python 3.11+ (for local development without Docker)

- **iOS:**
  - macOS with Xcode 15+
  - iOS Simulator or physical device

### Backend Setup

1. **Clone the repository:**
   ```bash
   cd /home/roman/luna_takehome_technical_interview
   ```

2. **Environment variables:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env if needed (defaults work for Docker Compose)
   ```

3. **Start services with Docker Compose:**
   ```bash
   cd ..
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL on port 5432
   - Start FastAPI on port 8000
   - Wait for database to be healthy before starting API

4. **Initialize database schema:**
   ```bash
   # In a new terminal
   docker-compose exec api python -c "from app.db import init_db; init_db()"
   ```

5. **Seed test data:**
   ```bash
   docker-compose exec db psql -U luna -d luna -f /app/seed_data.sql
   ```

   Or copy seed data into container:
   ```bash
   docker cp backend/seed_data.sql luna_db:/seed_data.sql
   docker-compose exec db psql -U luna -d luna -f /seed_data.sql
   ```

6. **Verify API is running:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

### iOS Setup

1. **Open Xcode project:**
   ```bash
   cd frontend
   open LunaTakeHome.xcodeproj
   ```

2. **Configure API endpoint:**
   - Open `LunaTakeHome/Config.swift`
   - Ensure `apiBaseURL` is set to `"http://127.0.0.1:8000"`
   - For physical device, use your Mac's local IP address

3. **Select target:**
   - Choose iPhone simulator (e.g., iPhone 15 Pro)
   - iOS 16.0+ required

4. **Build and run:**
   - Press Cmd+R or click the Play button
   - App should launch in simulator

---

## Running the Application

### Backend

**Start all services:**
```bash
docker-compose up
```

**Stop services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f api
```

**Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### iOS App

1. **Launch in Xcode** (Cmd+R)
2. **Select a test user** from the user selection screen
3. **Browse recommendations** in the Discover tab
4. **Tap a venue** to see details and recommended friends
5. **Confirm interest** to signal you want to go
6. **View plans** in the My Plans tab

### Testing Different Users

The app includes a user switcher:
1. Go to Profile tab
2. Tap "Switch User"
3. Select a different user to see their personalized recommendations

---

## Testing

### Backend Tests

**Run all tests:**
```bash
cd backend
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_recommendation.py -v
pytest tests/test_endpoints.py -v
```

**Test coverage:**
- Recommendation engine scoring algorithms
- Haversine distance calculations
- All API endpoints (CRUD operations)
- Agent reservation logic
- Error handling and validation

### Manual Testing Scenarios

1. **Recommendation Quality:**
   - Create users with different locations
   - Add friendships with varying strengths
   - Express interests in different venues
   - Verify recommendations are personalized

2. **Agent System:**
   - Have multiple users express interest in same venue
   - Confirm all users' interests
   - Verify automatic reservation creation

3. **iOS Integration:**
   - Test error states (disconnect backend)
   - Test loading states
   - Test pull-to-refresh
   - Test navigation flows

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Users

**GET /users**
- List all users
- Returns: `User[]`

**POST /users**
- Create a new user
- Body: `{ name, avatar_url?, bio? }`
- Returns: `User`

**GET /users/{user_id}**
- Get user by ID
- Returns: `User`

**GET /users/{user_id}/friends**
- Get user's friends with friendship strengths
- Returns: `Friendship[]`

#### Venues

**GET /venues**
- List venues with optional filters
- Query params: `category`, `min_lat`, `max_lat`, `min_lon`, `max_lon`
- Returns: `Venue[]`

**POST /venues**
- Create a venue
- Body: `{ name, category, address, latitude, longitude, description? }`
- Returns: `Venue`

#### Interests

**GET /users/{user_id}/interests**
- Get user's venue interests
- Returns: `UserInterest[]`

**POST /users/{user_id}/interests**
- Create or update interest
- Body: `{ venue_id, status }`
- Status: `INTERESTED | NOT_INTERESTED | INVITED | CONFIRMED`
- Returns: `UserInterest`

#### Recommendations

**GET /recommendations/{user_id}**
- Get personalized recommendations
- Query params: `lat?`, `lon?` (user's current location)
- Returns: `{ recommended_venues: [{ venue, score, recommended_people }] }`

#### Reservations

**GET /reservations/{user_id}**
- Get user's reservations
- Returns: `Reservation[]`

**POST /reservations**
- Create a reservation
- Body: `{ venue_id, time, participant_user_ids }`
- Returns: `Reservation`

**POST /reservations/accept**
- Accept a reservation invitation
- Body: `{ reservation_id, user_id }`
- Returns: `{ success, message, reservation? }`

---

## Design Decisions

### Backend Decisions

1. **FastAPI over Flask/Django:**
   - Native async/await support for better performance
   - Automatic OpenAPI documentation
   - Modern, type-safe Python with Pydantic

2. **PostgreSQL over MongoDB:**
   - Relational data model fits social graph and recommendations
   - ACID guarantees for reservation system
   - Mature ecosystem and tooling

3. **Service Layer Pattern:**
   - Separates business logic from API routes
   - Makes recommendation engine testable
   - Clean dependency injection

4. **No External ML Models:**
   - Deterministic scoring algorithm is explainable
   - No training data required
   - Fast response times (<100ms)
   - Easy to tune and debug

5. **Docker Compose for Local Dev:**
   - Consistent environment across machines
   - Easy database setup
   - Production-like configuration

### iOS Decisions

1. **MVVM Architecture:**
   - Required by assignment
   - Clean separation of concerns
   - Easy to test ViewModels
   - SwiftUI's natural pattern

2. **No Third-Party Libraries:**
   - URLSession is sufficient for HTTP
   - Codable handles JSON perfectly
   - Reduces app size and dependencies
   - No version conflicts

3. **Async/Await over Combine:**
   - Simpler error handling
   - More readable code
   - Standard Swift concurrency
   - Better debugging

4. **User Selection Screen:**
   - Enables testing different user perspectives
   - No authentication complexity for prototype
   - Demonstrates multi-user functionality

5. **Minimal Design:**
   - Focuses on functionality over aesthetics
   - System fonts and colors
   - Familiar iOS patterns
   - Fast to implement and modify

### Data Model Decisions

1. **Friendship Strength as Float:**
   - Allows nuanced social scoring
   - Could be derived from interaction frequency
   - Easy to extend with ML in future

2. **Interest Status Enum:**
   - Clear state machine: INTERESTED → CONFIRMED
   - Supports invitation flows
   - Enables agent triggers

3. **Reservation as Separate Entity:**
   - Tracks group decisions
   - Maintains history
   - Supports future features (payments, reviews)

---

## Use of Coding Agents

This project was implemented with assistance from **Claude Code** (Anthropic's AI coding assistant).

### Agent Usage Breakdown

1. **Backend Implementation (70% agent-assisted):**
   - Generated SQLAlchemy models based on requirements
   - Implemented recommendation scoring algorithms
   - Created FastAPI routers with proper validation
   - Wrote pytest test cases
   - Configured Docker and docker-compose files

2. **iOS Implementation (80% agent-assisted):**
   - Generated SwiftUI views following MVVM pattern
   - Implemented ViewModels with proper async/await
   - Created Codable models matching API schemas
   - Built APIClient with error handling
   - Generated Xcode project structure

3. **Documentation (90% agent-assisted):**
   - Structured README with all required sections
   - API documentation with examples
   - Architecture diagrams in ASCII art
   - Setup and deployment instructions

4. **Human Contributions:**
   - Overall architecture decisions
   - Product requirements interpretation
   - Design choices and trade-offs
   - Testing scenarios
   - Final review and validation

### Agent Prompts Used

Key prompts included:
- "Implement a haversine distance function for venue scoring"
- "Create a SwiftUI view with MVVM for venue recommendations"
- "Generate pytest tests for the recommendation engine"
- "Build a FastAPI endpoint with Pydantic validation"

---

## Deployment Considerations

### Google Cloud Run Deployment (Not Implemented)

The backend is designed to be Cloud Run compatible:

1. **Dockerfile is Cloud Run ready:**
   - Respects `PORT` environment variable
   - Stateless application design
   - No file system dependencies

2. **Deployment steps would be:**
   ```bash
   # Build and push container
   gcloud builds submit --tag gcr.io/PROJECT_ID/luna-api

   # Deploy to Cloud Run
   gcloud run deploy luna-api \
     --image gcr.io/PROJECT_ID/luna-api \
     --platform managed \
     --region us-central1 \
     --set-env-vars DATABASE_URL=postgresql://... \
     --allow-unauthenticated
   ```

3. **Database options:**
   - Cloud SQL for PostgreSQL (managed)
   - Connection via Cloud SQL Proxy
   - Or external PostgreSQL instance

4. **iOS configuration:**
   - Update `Config.swift` with Cloud Run URL
   - Use HTTPS for production

---

## Future Enhancements

### Track 1 Extensions
- Real-time location tracking
- Group chat for confirmed reservations
- Photo sharing and reviews
- Push notifications for invitations

### Track 2 Extensions
- Machine learning models trained on user behavior
- Time-based preference analysis
- Weather and event integration
- Natural language processing for venue descriptions

### Infrastructure
- CI/CD pipeline (GitHub Actions)
- Monitoring and alerting (Datadog/Sentry)
- Rate limiting and caching (Redis)
- Authentication (OAuth2/JWT)

---

## License

This project was created as a technical interview submission for Luna.

---

## Contact

**Candidate:** Roman
**Email:** [Your email]
**Submission Date:** November 23, 2025
**Video Demo:** [YouTube link to be added]
