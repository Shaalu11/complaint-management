# Hostel Complaint Management API

A FastAPI-based backend system for managing hostel complaints, student authentication, complaint tracking, notifications, and escalation.

---

## Features

- Student signup and login
- JWT authentication
- Password hashing
- Complaint creation
- Complaint retrieval
- Complaint update
- Complaint deletion
- Complaint search
- Complaint filtering
- Pagination
- Notification service
- Escalation service
- PostgreSQL database
- Alembic database migrations
- Automated testing
- Swagger/OpenAPI documentation
- Production-ready health checks
- Environment-based configuration

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12+ | Programming language |
| FastAPI | Backend web framework |
| SQLAlchemy | ORM |
| PostgreSQL | Database |
| Alembic | Database migrations |
| JWT | Authentication |
| Pydantic | Data validation |
| pytest | Testing |
| pytest-asyncio | Asynchronous testing |

---

## Project Structure

```text
hostel-complaint-management/
│
├── main.py
├── auth.py
├── database.py
├── db_models.py
├── schemas.py
├── notification_service.py
├── escalation_service.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   └── test_complaints.py
│
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── alembic.ini
├── requirements.txt
└── README.md
```

> **Note:** The `.env` file contains sensitive configuration and must not be committed to version control. Make sure `.env` is included in `.gitignore`.

---

## Requirements

Before running the project, make sure you have the following installed:

- Python 3.12+
- PostgreSQL
- pip
- Git
- Virtual environment support

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

Enter the project directory:

```bash
cd hostel-complaint-management
```

---

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

Activate the virtual environment:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root directory.

```env
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost/hostel_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

The database URL should contain your PostgreSQL username, password, host, and database name.

### Example `.env.example`

The repository includes an `.env.example` file containing placeholder values:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost/hostel_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

Copy the example configuration into a `.env` file and replace the placeholder values with your actual configuration.

> **Important:** Never commit `.env` or expose your secret keys publicly.

---

## Database Setup

### 1. Create the PostgreSQL Database

Create a PostgreSQL database named:

```text
hostel_db
```

You can create it using PostgreSQL:

```sql
CREATE DATABASE hostel_db;
```

---

### 2. Configure the Database

The application reads the PostgreSQL connection string from the `DATABASE_URL` environment variable.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost/hostel_db
```

---

### 3. Run Database Migrations

Apply the existing Alembic migrations:

```bash
alembic upgrade head
```

---

## Running the API

### Development

Start the FastAPI development server using:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger UI can be used to test the API endpoints directly from the browser.

---

# Authentication

The API uses **JWT Bearer Authentication**.

### 1. Register a Student

Send a request to:

```text
POST /signup
```

Example request:

```json
{
  "username": "student01",
  "password": "password123",
  "name": "Student One",
  "email": "student01@example.com",
  "room_number": "A101"
}
```

Example response:

```json
{
  "message": "Account created successfully",
  "username": "student01"
}
```

---

### 2. Login

Send a request to:

```text
POST /login
```

The endpoint uses form data.

Example:

```text
username=student01
password=password123
```

Example response:

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

---

### 3. Authorize Protected Endpoints

Protected endpoints require a valid JWT access token.

In Swagger UI:

1. Open `/docs`
2. Click **Authorize**
3. Enter the username and password used during login
4. Click **Authorize**
5. Swagger will use the JWT token for protected requests

Protected requests use the following authorization format:

```text
Authorization: Bearer <access_token>
```

---

# API Endpoints

## System

### Check API Health

```text
GET /health
```

Checks whether the API and PostgreSQL database are available.

### Healthy Response

```json
{
  "status": "healthy",
  "database": "connected"
}
```

If the database is unavailable:

```json
{
  "status": "unhealthy",
  "database": "unavailable"
}
```

---

# Authentication Endpoints

## Student Signup

```text
POST /signup
```

Creates a new student account.

### Example Request

```json
{
  "username": "student01",
  "password": "password123",
  "name": "Student One",
  "email": "student01@example.com",
  "room_number": "A101"
}
```

---

## Student Login

```text
POST /login
```

Authenticates a student and returns a JWT access token.

### Example Form Data

```text
username=student01
password=password123
```

### Example Response

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

---

# Complaint Endpoints

## Create a Complaint

```text
POST /complaints
```

Creates a complaint for the authenticated student.

### Authentication

```text
Authorization: Bearer <access_token>
```

### Example Request

```json
{
  "title": "Broken fan",
  "description": "The fan is not working",
  "category": "Electrical"
}
```

The student ID is automatically obtained from the authenticated user's JWT token.

---

## Get Complaints

```text
GET /complaints
```

Retrieves complaints belonging to the authenticated student.

### Supported Query Parameters

| Parameter | Description |
|-----------|-------------|
| `category` | Filter complaints by category |
| `status` | Filter complaints by status |
| `search` | Search complaint title and description |
| `skip` | Number of records to skip |
| `limit` | Maximum number of records to return |

### Filter by Category

```text
GET /complaints?category=Electrical
```

### Filter by Status

```text
GET /complaints?status=Pending
```

### Search Complaints

```text
GET /complaints?search=fan
```

### Pagination

```text
GET /complaints?skip=0&limit=10
```

---

## Get a Specific Complaint

```text
GET /complaints/{complaint_id}
```

Retrieves a specific complaint using its ID.

Example:

```text
GET /complaints/7
```

Requires a valid JWT access token.

Only the student who owns the complaint can access it.

---

## Update a Complaint

```text
PATCH /complaints/{complaint_id}
```

Updates an existing complaint.

Example:

```text
PATCH /complaints/7
```

### Example Request

```json
{
  "description": "The fan has completely stopped working",
  "status": "Pending"
}
```

Requires a valid JWT access token.

Only the student who owns the complaint can update it.

---

## Delete a Complaint

```text
DELETE /complaints/{complaint_id}
```

Deletes an existing complaint.

Example:

```text
DELETE /complaints/7
```

Requires a valid JWT access token.

Only the student who owns the complaint can delete it.

### Example Response

```json
{
  "message": "Complaint 7 deleted successfully"
}
```

---

# Testing

The project includes an automated test suite using `pytest` and `pytest-asyncio`.

Run the tests with:

```bash
pytest
```

The test suite uses an isolated asynchronous SQLite database for testing.

### Tests Cover

- Student signup
- Duplicate username validation
- Student login
- Invalid login
- Complaint creation
- Unauthorized requests
- Complaint ownership authorization
- Complaint search
- Complaint filtering
- Notification service integration

The expected result is:

```text
9 passed
```

---

# Database Migrations

The project uses **Alembic** for database schema migrations.

### Create a New Migration

After modifying the database models:

```bash
alembic revision --autogenerate -m "describe change"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Check Current Migration

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

---

# Deployment

## Production Startup

For development, the application can be started using:

```bash
uvicorn main:app --reload
```

For production-style execution, disable auto-reload:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The production startup command does not use the Uvicorn development reload option.

---

## Health Check

The `/health` endpoint checks both the FastAPI application and PostgreSQL database connection.

```text
GET /health
```

### Healthy Response

```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Unhealthy Response

```json
{
  "status": "unhealthy",
  "database": "unavailable"
}
```

This allows deployment environments to verify that the API and its database dependency are available.

---

## Environment Configuration

Sensitive configuration is stored using environment variables.

Required environment variables include:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost/hostel_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

The `.env` file must not be committed to source control.

The `.env.example` file can be committed because it contains only placeholder values.

---

# Application Flow

The basic complaint management workflow is:

```text
Student
   │
   ├── Sign Up
   │
   ├── Login
   │      │
   │      └── JWT Access Token
   │
   └── Manage Complaints
          │
          ├── Create Complaint
          ├── View Complaints
          ├── Search Complaints
          ├── Filter Complaints
          ├── Update Complaint
          └── Delete Complaint
```

When a complaint is created:

```text
Create Complaint
       │
       ├── Save to PostgreSQL
       │
       ├── Notification Service
       │
       └── Escalation Service
```

---

# Security

The application implements several security mechanisms:

- JWT-based authentication
- Password hashing
- Protected API endpoints
- Complaint ownership authorization
- Environment variables for sensitive configuration
- `.env` excluded from version control
- Student IDs are obtained from authenticated JWT tokens
- Students can only access their own complaints

---

# Development

To run the application during development:

```bash
uvicorn main:app --reload
```

After making changes to the database models, generate and apply a new migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Run the test suite before committing changes:

```bash
pytest
```

---

# Final Demonstration Flow

For a complete demonstration of the application:

1. Start PostgreSQL.
2. Apply database migrations.
3. Start the FastAPI application.
4. Open Swagger UI at `/docs`.
5. Register a new student using `/signup`.
6. Login using `/login`.
7. Authorize Swagger using the authenticated credentials.
8. Create a complaint using `/complaints`.
9. Verify the notification and escalation services.
10. Retrieve the complaint.
11. Test search and filtering.
12. Update the complaint.
13. Delete the complaint.
14. Verify the health endpoint.
15. Run the automated test suite using `pytest`.

---

# License

This project is developed for academic and educational purposes.