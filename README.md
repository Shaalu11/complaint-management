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

---

## Tech Stack

| Technology | Purpose |
|---|---|
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
├── .gitignore
├── pytest.ini
├── alembic.ini
├── requirements.txt
└── README.md
```

> **Note:** The `.env` file should not be committed to version control. Make sure `.env` is included in your `.gitignore`.

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

```powershell
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
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

If your application uses a PostgreSQL database URL, configure it according to your `database.py` configuration.

Example:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/hostel_db
```

> **Important:** Never commit your `.env` file or expose your secret keys publicly.

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

Configure the PostgreSQL connection in `database.py` or through the appropriate environment variables.

---

### 3. Run Database Migrations

Apply the existing Alembic migrations:

```bash
alembic upgrade head
```

---

## Running the API

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

---

## Authentication

The API uses **JWT Bearer Authentication**.

### 1. Register a Student

Send a request to:

```http
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

---

### 2. Login

Send a request to:

```http
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

For protected endpoints, provide the JWT token using:

```text
Authorization: Bearer <access_token>
```

In Swagger UI:

1. Open `/docs`
2. Click **Authorize**
3. Enter your access token
4. Click **Authorize**

---

# API Endpoints

## System

### Check API Health

```http
GET /health
```

Checks whether the API is running.

Example response:

```json
{
  "status": "success"
}
```

---

# Authentication Endpoints

## Student Signup

```http
POST /signup
```

Creates a new student account.

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

---

## Student Login

```http
POST /login
```

Authenticates a student and returns a JWT access token.

Example form data:

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

# Complaint Endpoints

## Create a Complaint

```http
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

---

## Get Complaints

```http
GET /complaints
```

Retrieves complaints.

### Supported Query Parameters

| Parameter | Description |
|---|---|
| `category` | Filter complaints by category |
| `status` | Filter complaints by status |
| `search` | Search complaints |
| `skip` | Number of records to skip |
| `limit` | Maximum number of records to return |

### Filter by Category

```http
GET /complaints?category=Electrical
```

### Filter by Status

```http
GET /complaints?status=Pending
```

### Search Complaints

```http
GET /complaints?search=fan
```

### Pagination

```http
GET /complaints?skip=0&limit=10
```

---

## Get a Specific Complaint

```http
GET /complaints/{complaint_id}
```

Retrieves a specific complaint using its ID.

Example:

```http
GET /complaints/7
```

### Authentication

Requires a valid JWT access token.

---

## Update a Complaint

```http
PATCH /complaints/{complaint_id}
```

Updates an existing complaint.

Example:

```http
PATCH /complaints/7
```

Example request:

```json
{
  "description": "The fan has completely stopped working",
  "status": "Pending"
}
```

### Authentication

Requires a valid JWT access token.

---

## Delete a Complaint

```http
DELETE /complaints/{complaint_id}
```

Deletes an existing complaint.

Example:

```http
DELETE /complaints/7
```

### Authentication

Requires a valid JWT access token.

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

---

# Database Migrations

The project uses **Alembic** for database schema migrations.

### Create a New Migration

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

# API Documentation

Interactive API documentation is automatically generated by FastAPI.

### Swagger UI

```text
/docs
```

### ReDoc

```text
/redoc
```

You can use Swagger UI to test the API endpoints directly from your browser.

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

---

# Security

The application implements several security mechanisms:

- JWT-based authentication
- Password hashing
- Protected API endpoints
- Complaint ownership authorization
- Environment variables for sensitive configuration
- `.env` excluded from version control

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

# License

This project is developed for academic and educational purposes.