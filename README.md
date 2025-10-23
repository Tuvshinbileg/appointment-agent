# 🤖 Appointment Booking Chat Agent

AI-powered booking system with Mongolian language support using FastAPI and OpenAI/Ollama.

## ✨ Features

- ✅ Natural language booking in Mongolian
- ✅ Intent classification (book, cancel, modify, check)
- ✅ Entity extraction (service, date, time, user info)
- ✅ Availability checking & conflict resolution
- ✅ Alternative time suggestions
- ✅ Persistent database storage (SQLite/PostgreSQL)
- ✅ FastAPI REST API
- ✅ OpenAI GPT-4 or Ollama support
- ✅ CLI mode for testing
- ✅ Comprehensive API documentation

## 📁 Project Structure

```
olhama-demo/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── bookings.db            # SQLite database (auto-created)
├── MIGRATION_GUIDE.md     # PostgreSQL migration guide
└── app/
    ├── __init__.py        # App package initialization
    ├── api/               # API routes
    │   ├── __init__.py
    │   └── routes.py      # FastAPI route handlers
    ├── core/              # Core business logic
    │   ├── __init__.py
    │   ├── booking_manager.py  # Booking operations
    │   └── chat_agent.py       # AI chat agent
    ├── database/          # Database layer
    │   ├── __init__.py
    │   ├── database.py    # SQLAlchemy setup
    │   └── models.py      # Database models
    ├── models/            # Data models
    │   ├── __init__.py
    │   └── schemas.py     # Pydantic schemas
    └── utils/             # Utility functions
        ├── __init__.py
        └── parsers.py     # Date/time parsers
```

## 🚀 Installation

### 1. Clone the repository

```bash
cd /path/to/olhama-demo
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (OpenAI API key, etc.)
```

## 🎯 Usage

### API Mode (Default)

Run the FastAPI server:

```bash
python main.py
```

The server will start at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### CLI Mode

Run in command-line interface mode for testing:

```bash
python main.py cli
```

Available commands:
- Type your message to chat with the agent
- `bookings` - View your bookings
- `clear` - Reset conversation
- `exit` - Quit the application

## 📡 API Endpoints

### Chat
- `POST /chat` - Chat with the booking agent

### Bookings
- `GET /bookings` - List all bookings (with filters)
- `GET /bookings/{booking_id}` - Get specific booking
- `POST /bookings` - Create booking directly
- `DELETE /bookings/{booking_id}` - Cancel booking

### Availability
- `GET /availability` - Check time slot availability

### Session
- `DELETE /clear-session/{session_id}` - Clear conversation history

### Utility
- `GET /` - API information
- `GET /health` - Health check

## 💬 Example Interactions

### Mongolian (Native)

```
User: Маргааш 10:00-д үс засалт захиалмаар байна
Agent: Би шалгаж байна... Тэр цагт сул байна. Таны нэр болон утасны дугаар?

User: Батаа, 99112233
Agent: Баярлалаа Батаа! Таны үс засалтын цаг 2025-10-24 10:00-д амжилттай батлагдлаа.

User: Миний захиалгуудыг харуулаарай
Agent: [Shows list of bookings]

User: Захиалгаа цуцлаарай
Agent: Та 2025-10-24 10:00-д хийсэн үс засалтын захиалгаа цуцлахыг хүсэж байна уу?
```

### English (For Testing)

```
User: I want to book a haircut tomorrow at 2 PM
Agent: Let me check... That time is available. What's your name and phone number?

User: John, 12345678
Agent: Thank you John! Your haircut appointment is confirmed for 2025-10-24 14:00.
```

## 🔧 Configuration

Edit `config.py` or set environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./bookings.db` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `USE_OPENAI` | Use OpenAI (true) or Ollama (false) | `true` |
| `OPENAI_API_KEY` | Your OpenAI API key | Required for OpenAI |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `OLLAMA_MODEL` | Ollama model to use | `gemma3` |
| `BUSINESS_START_HOUR` | Business start time (24h) | `9` |
| `BUSINESS_END_HOUR` | Business end time (24h) | `18` |

## 🏗️ Architecture

### Core Components

1. **BookingManager** (`app/core/booking_manager.py`)
   - Manages all booking operations
   - Handles data persistence (JSON)
   - Checks availability and suggests alternatives

2. **ChatAgent** (`app/core/chat_agent.py`)
   - Processes natural language messages
   - Handles function calling with LLMs
   - Maintains conversation context

3. **API Routes** (`app/api/routes.py`)
   - FastAPI endpoint handlers
   - Request/response validation
   - Error handling

4. **Data Models** (`app/models/schemas.py`)
   - Pydantic models for validation
   - Type safety and documentation

5. **Utilities** (`app/utils/parsers.py`)
   - Date/time parsing
   - Text extraction helpers

### Data Flow

```
User Message → API Endpoint → ChatAgent → LLM (OpenAI/Ollama)
                                ↓
                         Function Calling
                                ↓
                         BookingManager
                                ↓
                         JSON Storage
                                ↓
                         Response → User
```

## 🧪 Testing

### Test with curl

```bash
# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Маргааш 10:00-д үс засалт захиалмаар байна", "user_id": "test_user"}'

# Check availability
curl "http://localhost:8000/availability?date=2025-10-24&time=10:00&duration=60"

# List bookings
curl "http://localhost:8000/bookings?user_id=test_user"
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Маргааш 10:00-д үс засалт захиалмаар байна",
        "user_id": "test_user"
    }
)
print(response.json())
```

## 💾 Database

### SQLite (Default)

The application uses SQLite by default, which requires no setup:
```bash
DATABASE_URL=sqlite:///./bookings.db
```

### PostgreSQL (Production)

For production deployments, switch to PostgreSQL:

1. Install PostgreSQL
2. Create database and user
3. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/booking_db
   ```
4. Restart application

See **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** for detailed instructions.

### Database Features

- ✅ Automatic table creation
- ✅ Indexed queries for performance
- ✅ Transaction support
- ✅ Easy migration between SQLite and PostgreSQL
- ✅ SQLAlchemy ORM for database abstraction

## 🐛 Troubleshooting

### "Neither OpenAI nor Ollama is available"
- Install one: `pip install openai` or `pip install ollama`
- Set `USE_OPENAI=true` in `.env` and provide API key

### "Database connection error"
- Check DATABASE_URL in `.env`
- Ensure database file/server is accessible
- For PostgreSQL: verify server is running

### "Port 8000 already in use"
- Change port: `API_PORT=8001` in `.env`
- Or kill existing process: `lsof -ti:8000 | xargs kill -9`

## 📝 Available Services

Default services configured in `config.py`:

- үс засалт (Haircut) - 60 min
- шүдний үзлэг (Dental checkup) - 45 min
- массаж (Massage) - 90 min
- маникюр (Manicure) - 45 min
- педикюр (Pedicure) - 60 min
- косметик (Cosmetics) - 120 min
- эмчилгээ (Medical treatment) - 60 min
- сэтгэл зүйч (Psychology) - 60 min

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use for any purpose

## 👨‍💻 Authors

AI Booking Team

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

Made with ❤️ using FastAPI, OpenAI, and Python
