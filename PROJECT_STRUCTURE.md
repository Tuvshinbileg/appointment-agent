# Project Structure

This document explains the architecture and organization of the Appointment Booking Chat Agent.

## Overview

```
olhama-demo/
├── main.py                     # Application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── MIGRATION_GUIDE.md          # PostgreSQL migration guide
├── PROJECT_STRUCTURE.md        # This file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── bookings.db                 # SQLite database (auto-generated)
└── app/                        # Main application package
    ├── __init__.py
    ├── api/                    # API layer
    │   ├── __init__.py
    │   └── routes.py           # FastAPI route handlers
    ├── core/                   # Business logic layer
    │   ├── __init__.py
    │   ├── booking_manager.py  # Booking operations
    │   └── chat_agent.py       # AI chat agent with LLM integration
    ├── database/               # Database layer (NEW!)
    │   ├── __init__.py
    │   ├── database.py         # SQLAlchemy configuration
    │   └── models.py           # Database models
    ├── models/                 # Data models layer
    │   ├── __init__.py
    │   └── schemas.py          # Pydantic schemas for validation
    └── utils/                  # Utilities layer
        ├── __init__.py
        └── parsers.py          # Date/time parsing functions
```

## Architecture Layers

### 1. Entry Point (`main.py`)

**Purpose:** Application startup and mode selection

**Responsibilities:**
- Initialize database on startup
- Create FastAPI application
- Configure middleware (CORS)
- Run server or CLI mode
- Dependency injection setup

**Key Functions:**
- `create_app()` - Creates and configures FastAPI app
- `run_server()` - Starts the API server
- `run_cli()` - Starts CLI testing mode

### 2. Configuration (`config.py`)

**Purpose:** Centralized configuration management

**Settings:**
- Database connection URL
- API server settings
- LLM backend configuration (OpenAI/Ollama)
- Business hours
- Service definitions
- CORS settings

**Environment Variables:**
All settings can be overridden via environment variables or `.env` file.

### 3. Database Layer (`app/database/`)

**Purpose:** Database abstraction and ORM

#### `database.py`
- SQLAlchemy engine setup
- Session management
- Database initialization
- Supports both SQLite and PostgreSQL

#### `models.py`
- `BookingDB` - SQLAlchemy model for bookings table
- Includes indexes for performance
- `to_dict()` method for serialization

**Features:**
- ✅ Automatic table creation
- ✅ Transaction support
- ✅ Easy switching between SQLite/PostgreSQL
- ✅ Indexed queries for performance

### 4. Core Business Logic (`app/core/`)

#### `booking_manager.py`

**Purpose:** Manages all booking operations

**Key Methods:**
- `check_availability()` - Checks if time slot is available
- `suggest_alternatives()` - Suggests alternative time slots
- `create_booking()` - Creates new booking with validation
- `cancel_booking()` - Cancels booking by ID or user
- `list_bookings()` - Lists bookings with filters
- `get_booking()` - Gets specific booking

**Database Integration:**
- Uses SQLAlchemy sessions
- Proper transaction management
- Error handling with rollback

#### `chat_agent.py`

**Purpose:** AI-powered conversational interface

**Key Features:**
- Natural language processing
- Function calling with LLMs
- Conversation history management
- Date/time parsing from Mongolian text
- Integration with BookingManager

**Supported LLMs:**
- OpenAI (GPT-4, GPT-3.5-turbo) with function calling
- Ollama (Gemma3, etc.) - basic mode

**Methods:**
- `process_message()` - Main message processing
- `_call_llm()` - LLM API calls
- `_execute_function()` - Execute booking functions
- `clear_history()` - Clear conversation history

### 5. API Layer (`app/api/`)

#### `routes.py`

**Purpose:** FastAPI endpoint definitions

**Endpoints:**

**Chat:**
- `POST /chat` - Conversational booking

**Bookings:**
- `GET /bookings` - List all bookings (with filters)
- `GET /bookings/{id}` - Get specific booking
- `POST /bookings` - Create booking directly
- `DELETE /bookings/{id}` - Cancel booking

**Utilities:**
- `GET /availability` - Check time slot availability
- `DELETE /clear-session/{id}` - Clear conversation history
- `GET /health` - Health check
- `GET /` - API information

**Features:**
- Request/response validation with Pydantic
- Proper error handling with HTTP status codes
- Dependency injection for managers

### 6. Data Models (`app/models/`)

#### `schemas.py`

**Purpose:** Pydantic models for API validation

**Models:**
- `ChatMessage` - Incoming chat message
- `ChatResponse` - Chat agent response
- `BookingCreate` - Booking creation request
- `Booking` - Complete booking data
- `AvailabilityCheck` - Availability check request

**Benefits:**
- Automatic validation
- Type safety
- API documentation generation
- Serialization/deserialization

### 7. Utilities (`app/utils/`)

#### `parsers.py`

**Purpose:** Helper functions for text parsing

**Functions:**
- `parse_date_mongolian()` - Parse Mongolian date expressions
- `parse_time()` - Extract time from text
- `extract_phone_number()` - Extract phone numbers
- `extract_service()` - Extract service type

## Data Flow

### 1. API Request Flow

```
User Request
    ↓
FastAPI Endpoint (routes.py)
    ↓
Pydantic Validation (schemas.py)
    ↓
ChatAgent or BookingManager (core/)
    ↓
Database Operations (database/)
    ↓
SQLAlchemy ORM (models.py)
    ↓
SQLite/PostgreSQL Database
    ↓
Response to User
```

### 2. Chat Flow

```
User Message
    ↓
ChatAgent.process_message()
    ↓
LLM (OpenAI/Ollama)
    ↓
Function Call Detection
    ↓
BookingManager Method Execution
    ↓
Database Operation
    ↓
Response Generation
    ↓
User sees Response
```

### 3. Booking Creation Flow

```
User: "Маргааш 10:00-д үс засалт"
    ↓
ChatAgent parses: date=2025-10-24, time=10:00, service=үс засалт
    ↓
LLM generates function call: create_booking()
    ↓
BookingManager.check_availability()
    ↓
Database query for conflicts
    ↓
If available:
    BookingManager.create_booking()
    Database INSERT
    Return success
Else:
    BookingManager.suggest_alternatives()
    Return alternatives
    ↓
ChatAgent generates Mongolian response
    ↓
User sees confirmation or alternatives
```

## Design Patterns

### 1. **Layered Architecture**
- Clear separation of concerns
- Each layer has specific responsibility
- Easy to test and maintain

### 2. **Dependency Injection**
- Managers injected into routes
- Easy to mock for testing
- Flexible configuration

### 3. **Repository Pattern**
- BookingManager acts as repository
- Abstracts database operations
- Easy to swap implementations

### 4. **Factory Pattern**
- `create_app()` creates configured app
- Easy to create test instances

### 5. **Singleton Pattern**
- Database engine is singleton
- Single connection pool

## Database Schema

### `bookings` Table

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| id | VARCHAR (PK) | Unique booking ID (UUID) | Yes |
| user_id | VARCHAR | User identifier | Yes |
| user_name | VARCHAR | User's name | No |
| phone | VARCHAR | Phone number | No |
| service | VARCHAR | Service type | No |
| date | VARCHAR | Date (YYYY-MM-DD) | Yes |
| time | VARCHAR | Time (HH:MM) | No |
| duration_minutes | INTEGER | Duration in minutes | No |
| status | VARCHAR | Status (confirmed/cancelled) | Yes |
| created_at | TIMESTAMP | Creation timestamp | No |
| updated_at | TIMESTAMP | Last update timestamp | No |

**Indexes:**
- Primary Key: `id`
- Index on: `user_id`, `date`, `status`

## Configuration Management

### Environment Variables (Priority Order)

1. **System Environment Variables** (highest priority)
2. **`.env` File** (middle priority)
3. **Default Values in `config.py`** (lowest priority)

### Key Configurations

```python
# Database
DATABASE_URL = "sqlite:///./bookings.db"  # or PostgreSQL URL

# API
API_HOST = "0.0.0.0"
API_PORT = 8000

# LLM
USE_OPENAI = True
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4"

# Business
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 18
```

## Error Handling

### Database Errors
- Automatic rollback on exceptions
- Graceful error messages
- Transaction safety

### API Errors
- HTTP status codes (400, 404, 500)
- Detailed error messages
- No sensitive data leakage

### LLM Errors
- Fallback messages
- Retry logic (implicit in max_iterations)
- Graceful degradation

## Testing Strategy

### Unit Tests (Future)
```python
# test_booking_manager.py
def test_check_availability():
    manager = BookingManager()
    result = manager.check_availability("2025-10-24", "10:00")
    assert result['available'] == True
```

### Integration Tests (Future)
```python
# test_api.py
def test_chat_endpoint():
    response = client.post("/chat", json={"message": "Маргааш 10:00"})
    assert response.status_code == 200
```

### CLI Testing (Current)
```bash
python main.py cli
# Manual testing through command line
```

## Performance Considerations

### Database
- Indexed columns for fast queries
- Connection pooling via SQLAlchemy
- Prepared statements (SQL injection protection)

### API
- Async support ready (FastAPI)
- Connection pooling
- CORS configured for cross-origin requests

### Caching (Future Enhancement)
- Cache availability checks
- Redis for session storage
- LRU cache for common queries

## Security

### Database
- SQL injection protection (SQLAlchemy ORM)
- Parameterized queries
- Transaction isolation

### API
- CORS middleware
- Input validation (Pydantic)
- No hardcoded credentials

### Best Practices
- Environment variables for secrets
- `.env` in `.gitignore`
- Separate user permissions (PostgreSQL)

## Extensibility

### Adding New Endpoints
1. Define Pydantic schema in `app/models/schemas.py`
2. Add route in `app/api/routes.py`
3. Implement logic in `app/core/`

### Adding New Services
1. Update `SERVICES` dict in `config.py`
2. No code changes needed!

### Adding New LLM Provider
1. Add client initialization in `chat_agent.py`
2. Implement `_call_llm()` for new provider
3. Add configuration in `config.py`

### Adding New Database
1. Update `DATABASE_URL` in config
2. Install appropriate driver
3. SQLAlchemy handles the rest!

## Migration Path

### From JSON to SQLite (✅ Completed)
- Database layer implemented
- BookingManager uses SQLAlchemy
- Backward compatible

### From SQLite to PostgreSQL (🔄 Ready)
1. Set up PostgreSQL server
2. Update `DATABASE_URL` in `.env`
3. Restart application
4. See MIGRATION_GUIDE.md

### Adding Alembic (📋 Planned)
- Schema version control
- Automated migrations
- Rollback support

## Maintenance

### Database Backups

**SQLite:**
```bash
cp bookings.db backups/bookings_$(date +%Y%m%d).db
```

**PostgreSQL:**
```bash
pg_dump booking_db > backups/booking_db_$(date +%Y%m%d).sql
```

### Log Rotation
- Configure uvicorn logging
- Rotate log files
- Monitor disk usage

### Monitoring
- Health check endpoint: `/health`
- Database connection status
- API response times

## Future Enhancements

### Short Term
- [ ] Add authentication (JWT)
- [ ] Email notifications
- [ ] SMS confirmations
- [ ] Admin dashboard

### Medium Term
- [ ] Multi-tenant support
- [ ] Calendar integration
- [ ] Payment processing
- [ ] Waitlist management

### Long Term
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] ML-powered scheduling optimization

## Contributing

When contributing code:
1. Follow existing structure
2. Add appropriate layer
3. Update documentation
4. Write tests
5. Follow Python PEP 8 style

## Support

For questions about the architecture:
- Read this document
- Check README.md
- Review MIGRATION_GUIDE.md
- Examine code comments

---

**Last Updated:** 2025-10-23  
**Version:** 1.0.0  
**Architecture:** Layered + Repository Pattern  
**Database:** SQLite/PostgreSQL via SQLAlchemy
