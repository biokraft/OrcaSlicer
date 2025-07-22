# Phase 5: Database Persistence Implementation Plan (Parallel Tracks)

## Overview
Implement database persistence for chat conversations using SQLite, SQLAlchemy, and Alembic. This plan is structured into parallel development tracks that can be worked on simultaneously, converging in a final integration track.

## Parallel Development Tracks

### 🔧 Track A: Dependencies & Configuration
**Goal**: Set up all database-related dependencies and configuration
**Prerequisites**: None
**Can be developed in parallel with**: Track B, Track C

#### A1: Database Dependencies Setup
- [ ] **Write failing test: Test dependencies import correctly**
- [ ] **Implement: Add database dependencies to pyproject.toml**
  - SQLAlchemy >= 2.0.0 (async support)
  - Alembic >= 1.13.0 (migrations)
  - aiosqlite >= 0.19.0 (async SQLite driver)
- [ ] **Test: Verify dependencies are properly installed and importable**

#### A2: Database Configuration
- [ ] **Write failing test: Test database configuration settings validation**
- [ ] **Implement: Add database settings to Config class**
  - `database_url: str` (default: "sqlite+aiosqlite:///./orca_agents.db")
  - `database_path: Path` (default: "./data/orca_agents.db")
  - `enable_persistence: bool` (default: True)
  - `database_pool_size: int` (default: 5)
  - `database_timeout: int` (default: 30)
- [ ] **Test: Verify configuration loads and validates correctly**

### 🗃️ Track B: Database Models & Schemas
**Goal**: Create all data models and validation schemas
**Prerequisites**: None
**Can be developed in parallel with**: Track A, Track C

#### B1: SQLAlchemy Database Models
- [ ] **Write failing test: Test Conversation model creation and relationships**
- [ ] **Implement: Create Conversation SQLAlchemy model**
  ```python
  class Conversation(Base):
      id: UUID (Primary Key)
      created_at: datetime
      updated_at: datetime
      title: str
      messages: relationship to Message
  ```
- [ ] **Write failing test: Test Message model creation and relationships**
- [ ] **Implement: Create Message SQLAlchemy model**
  ```python
  class Message(Base):
      id: UUID (Primary Key)
      conversation_id: UUID (Foreign Key)
      role: str ('user', 'assistant', 'system')
      content: str
      timestamp: datetime
      metadata: JSON (tool calls, agent info, etc.)
      conversation: relationship to Conversation
  ```
- [ ] **Test: Verify models work correctly with SQLAlchemy**

#### B2: Pydantic Response Schemas
- [ ] **Write failing test: Test Pydantic models serialize/deserialize correctly**
- [ ] **Implement: Create Pydantic schemas for API responses**
  ```python
  class MessageResponse(BaseModel)
  class ConversationResponse(BaseModel)
  class ConversationSummary(BaseModel)
  class ConversationListResponse(BaseModel)
  ```
- [ ] **Test: Verify Pydantic models handle all edge cases**

### 🔌 Track C: Database Engine & Migrations
**Goal**: Set up database connection and migration system
**Prerequisites**: None
**Can be developed in parallel with**: Track A, Track B

#### C1: Database Engine and Session Management
- [ ] **Write failing test: Test async database engine creation**
- [ ] **Implement: Create async database engine factory**
  - Async SQLAlchemy engine
  - Session factory with proper lifecycle
  - Connection pooling configuration
- [ ] **Write failing test: Test database session lifecycle**
- [ ] **Implement: Database session management with async context managers**
- [ ] **Test: Verify database connections work correctly**

#### C2: Alembic Migration Setup
- [ ] **Write failing test: Test migration directory structure exists**
- [ ] **Implement: Initialize Alembic for async SQLAlchemy**
  - Configure `alembic.ini` for async operations
  - Set up `env.py` with proper async configuration
  - Create migrations directory structure
- [ ] **Write failing test: Test initial migration generation**
- [ ] **Implement: Generate and test initial migration**
  - Create tables for Conversation and Message
  - Add proper indexes and constraints
- [ ] **Test: Verify migration applies and reverts successfully**

### 🔄 Track D: Service Layer
**Goal**: Create business logic layer for database operations
**Prerequisites**: Track B (models must exist)
**Can be developed in parallel with**: Track E (after B is complete)

#### D1: Core Service Operations
- [ ] **Write failing test: Test conversation creation**
- [ ] **Implement: ConversationService.create_conversation(title: str) -> Conversation**
- [ ] **Write failing test: Test message saving**
- [ ] **Implement: ConversationService.save_message(conversation_id, role, content, metadata)**
- [ ] **Write failing test: Test conversation retrieval**
- [ ] **Implement: ConversationService.get_conversation(id) -> Conversation with messages**
- [ ] **Test: Verify core operations work correctly**

#### D2: Advanced Service Operations
- [ ] **Write failing test: Test conversation listing with pagination**
- [ ] **Implement: ConversationService.list_conversations(limit, offset) -> List[ConversationSummary]**
- [ ] **Write failing test: Test conversation deletion**
- [ ] **Implement: ConversationService.delete_conversation(id) -> bool**
- [ ] **Write failing test: Test conversation title auto-generation**
- [ ] **Implement: ConversationService.generate_title_from_message(content) -> str**
- [ ] **Test: Verify all advanced operations work correctly**

### 🌐 Track E: API Endpoints
**Goal**: Create REST API endpoints for conversation management
**Prerequisites**: Track B (schemas must exist)
**Can be developed in parallel with**: Track D (after B is complete)

#### E1: Read-Only API Endpoints
- [ ] **Write failing test: Test GET /api/conversations endpoint**
- [ ] **Implement: List conversations endpoint with pagination**
  ```python
  GET /api/conversations?limit=10&offset=0
  Response: ConversationListResponse
  ```
- [ ] **Write failing test: Test GET /api/conversations/{id} endpoint**
- [ ] **Implement: Get specific conversation with messages**
  ```python
  GET /api/conversations/{id}
  Response: ConversationResponse
  ```
- [ ] **Test: Verify read-only endpoints work correctly**

#### E2: Modification API Endpoints
- [ ] **Write failing test: Test DELETE /api/conversations/{id} endpoint**
- [ ] **Implement: Delete conversation endpoint**
  ```python
  DELETE /api/conversations/{id}
  Response: 204 No Content
  ```
- [ ] **Write failing test: Test PUT /api/conversations/{id} endpoint**
- [ ] **Implement: Update conversation title endpoint**
  ```python
  PUT /api/conversations/{id}
  Request: {"title": "New Title"}
  Response: ConversationResponse
  ```
- [ ] **Test: Verify modification endpoints work correctly**

## 🔀 Integration Track: Final Assembly
**Goal**: Integrate all tracks into a working system
**Prerequisites**: All tracks A, B, C, D, E must be complete

### I1: Database Integration with Application
- [ ] **Write failing test: Test database initialization in FastAPI startup**
- [ ] **Implement: Integrate database engine with FastAPI lifecycle**
  - Add database startup/shutdown events
  - Initialize migrations on startup
  - Configure dependency injection for database sessions
- [ ] **Write failing test: Test database dependency injection in endpoints**
- [ ] **Implement: Connect API endpoints to service layer**
- [ ] **Test: Verify database works with FastAPI application**

### I2: Chat Flow Integration
- [ ] **Write failing test: Test conversation persistence during chat**
- [ ] **Implement: Integrate ConversationService into MultiAgentOrchestrator**
  - Auto-create conversations for new chats
  - Save user messages before processing
  - Save assistant responses after generation
  - Handle conversation_id in chat requests
- [ ] **Write failing test: Test modified chat endpoint with persistence**
- [ ] **Implement: Update chat endpoint to handle conversation persistence**
- [ ] **Test: Verify chat messages are automatically saved**

### I3: Error Handling and Resilience
- [ ] **Write failing test: Test graceful degradation when database unavailable**
- [ ] **Implement: Fallback behavior for database failures**
  - Chat continues to work even if persistence fails
  - Proper error logging and user notification
  - Health check integration for database status
- [ ] **Write failing test: Test handling of invalid conversation IDs**
- [ ] **Implement: Proper error responses and validation**
- [ ] **Test: Verify application remains stable during database issues**

### I4: End-to-End Integration Tests
- [ ] **Write failing test: Test complete conversation lifecycle**
- [ ] **Implement: Full workflow test (create -> chat -> retrieve -> delete)**
- [ ] **Write failing test: Test multiple concurrent conversations**
- [ ] **Implement: Concurrent conversation handling**
- [ ] **Write failing test: Test application restart with existing conversations**
- [ ] **Implement: Proper state persistence across restarts**
- [ ] **Test: Verify complete system integration**

### I5: Performance and Production Readiness
- [ ] **Write failing test: Test database query performance with large datasets**
- [ ] **Implement: Database indexes and query optimization**
- [ ] **Write failing test: Test concurrent access to conversations**
- [ ] **Implement: Proper connection pooling and transaction handling**
- [ ] **Write failing test: Test memory usage during long conversations**
- [ ] **Implement: Efficient pagination and memory management**
- [ ] **Test: Verify performance meets production requirements**

## Development Strategy

### Parallel Execution Plan
1. **Phase 1**: Start Tracks A, B, C simultaneously (independent)
2. **Phase 2**: Once B is complete, start Tracks D and E (both depend on B)
3. **Phase 3**: Once all tracks A-E are complete, begin Integration Track I

### Dependencies Map
```
Track A (Config) ────┐
                     ├─── Integration Track I
Track B (Models) ────┼─── Track D (Service)
                     ├─── Track E (API)
Track C (Engine) ────┘
```

### File Structure
```
orca_agents/
├── database/
│   ├── __init__.py
│   ├── models.py          # Track B
│   ├── schemas.py         # Track B
│   ├── engine.py          # Track C
│   └── service.py         # Track D
├── migrations/            # Track C
│   ├── versions/
│   ├── alembic.ini
│   └── env.py
tests/
└── database/
    ├── __init__.py
    ├── test_models.py     # Track B
    ├── test_service.py    # Track D
    ├── test_api.py        # Track E
    └── test_integration.py # Integration Track I
```

## Success Criteria
- [ ] All tracks A-E complete independently
- [ ] Integration track successfully merges all components
- [ ] All conversations automatically saved to database
- [ ] Users can retrieve conversation history via API
- [ ] Database migrations work correctly
- [ ] Application gracefully handles database failures
- [ ] 95%+ test coverage for database components
- [ ] Complete end-to-end conversation workflows tested and working
