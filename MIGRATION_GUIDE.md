# Database Migration Guide

This guide explains how to switch from SQLite to PostgreSQL.

## Current Setup (SQLite)

By default, the application uses SQLite with the database file at `./bookings.db`.

**Configuration:**
```bash
DATABASE_URL=sqlite:///./bookings.db
```

## Switching to PostgreSQL

### Step 1: Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Step 2: Create Database and User

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE booking_db;

# Create user with password
CREATE USER booking_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE booking_db TO booking_user;

# Exit
\q
```

### Step 3: Update Configuration

Edit your `.env` file or environment variables:

```bash
# Comment out SQLite
# DATABASE_URL=sqlite:///./bookings.db

# Add PostgreSQL
DATABASE_URL=postgresql://booking_user:your_secure_password@localhost:5432/booking_db
```

### Step 4: Install PostgreSQL Driver

The `psycopg2-binary` package is already in requirements.txt, but if you need to install it separately:

```bash
pip install psycopg2-binary
```

### Step 5: Restart Application

```bash
python main.py
```

The database tables will be automatically created on first run.

## Data Migration (SQLite → PostgreSQL)

If you have existing data in SQLite that you want to migrate to PostgreSQL:

### Option 1: Export/Import Script

Create a migration script (`migrate_data.py`):

```python
#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import BookingDB, Base

# Source (SQLite)
sqlite_url = "sqlite:///./bookings.db"
sqlite_engine = create_engine(sqlite_url)
SQLiteSession = sessionmaker(bind=sqlite_engine)

# Destination (PostgreSQL)
postgres_url = "postgresql://booking_user:password@localhost:5432/booking_db"
postgres_engine = create_engine(postgres_url)
PostgresSession = sessionmaker(bind=postgres_engine)

# Create tables in PostgreSQL
Base.metadata.create_all(postgres_engine)

# Migrate data
sqlite_session = SQLiteSession()
postgres_session = PostgresSession()

try:
    # Read all bookings from SQLite
    bookings = sqlite_session.query(BookingDB).all()
    
    print(f"Found {len(bookings)} bookings to migrate")
    
    # Insert into PostgreSQL
    for booking in bookings:
        postgres_booking = BookingDB(
            id=booking.id,
            user_id=booking.user_id,
            user_name=booking.user_name,
            phone=booking.phone,
            service=booking.service,
            date=booking.date,
            time=booking.time,
            duration_minutes=booking.duration_minutes,
            status=booking.status,
            created_at=booking.created_at
        )
        postgres_session.add(postgres_booking)
    
    postgres_session.commit()
    print("✅ Migration completed successfully!")
    
except Exception as e:
    postgres_session.rollback()
    print(f"❌ Migration failed: {e}")
finally:
    sqlite_session.close()
    postgres_session.close()
```

Run the migration:
```bash
python migrate_data.py
```

### Option 2: Using pgloader

Install pgloader:
```bash
sudo apt install pgloader  # Ubuntu/Debian
brew install pgloader      # macOS
```

Create a migration config file (`migration.load`):
```
LOAD DATABASE
     FROM sqlite:///bookings.db
     INTO postgresql://booking_user:password@localhost/booking_db

WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '16MB', maintenance_work_mem to '512 MB';
```

Run migration:
```bash
pgloader migration.load
```

## Database Schema

The application uses the following table structure:

```sql
CREATE TABLE bookings (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    user_name VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    service VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    time VARCHAR NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status VARCHAR DEFAULT 'confirmed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_date ON bookings(date);
CREATE INDEX idx_bookings_status ON bookings(status);
```

## Testing the Migration

After migration, test the application:

```bash
# Run in CLI mode
python main.py cli

# Try creating a booking
# Check existing bookings with 'bookings' command
```

Or test via API:
```bash
# Start server
python main.py

# Test endpoint
curl http://localhost:8000/bookings
```

## Rollback

To rollback to SQLite:

1. Stop the application
2. Update `.env`:
   ```bash
   DATABASE_URL=sqlite:///./bookings.db
   ```
3. Restart application

## Performance Considerations

### SQLite
- ✅ Simple, no server needed
- ✅ Good for development and small deployments
- ❌ Limited concurrent write operations
- ❌ Not suitable for high-traffic production

### PostgreSQL
- ✅ Excellent for production
- ✅ Handles concurrent connections well
- ✅ Advanced features (JSON, full-text search, etc.)
- ✅ Better performance at scale
- ❌ Requires server setup and maintenance

## Troubleshooting

### "psycopg2" not found
```bash
pip install psycopg2-binary
```

### Connection refused
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Start PostgreSQL: `sudo systemctl start postgresql`
- Check connection settings in DATABASE_URL

### Authentication failed
- Verify username and password
- Check pg_hba.conf for authentication method
- Ensure user has proper privileges

### Database does not exist
```bash
sudo -u postgres psql
CREATE DATABASE booking_db;
```

## Using Alembic for Migrations (Advanced)

For production environments, use Alembic for schema migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Cloud Database Options

### AWS RDS
```bash
DATABASE_URL=postgresql://username:password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/booking_db
```

### Google Cloud SQL
```bash
DATABASE_URL=postgresql://username:password@/booking_db?host=/cloudsql/project:region:instance
```

### Heroku Postgres
```bash
DATABASE_URL=postgres://username:password@hostname:5432/database
```

### DigitalOcean Managed Database
```bash
DATABASE_URL=postgresql://username:password@hostname:25060/booking_db?sslmode=require
```

## Support

For issues or questions, refer to:
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [FastAPI Database Documentation](https://fastapi.tiangolo.com/tutorial/sql-databases/)
