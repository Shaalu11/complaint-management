# Hostel Complaint Management API

## Entities

### Student

- id
- name
- email
- room_number

### Complaint

- id
- title
- description
- category
- status
- student_id
- created_at

## Relationship

One student can submit multiple complaints.

One complaint belongs to one student.

Relationship:

Student (1) ---- (Many) Complaint

## Complaint Status

- Pending
- In Progress
- Resolved

## Complaint Categories

- Electrical
- Plumbing
- Food
- Cleaning
- WiFi
- Other

## API Endpoints (just a blueprint for now)

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Check API health |
| POST | /complaints | Create complaint |
| GET | /complaints | Get all complaints |
| GET | /complaints/{id} | Get complaint by ID |
| PUT | /complaints/{id} | Update complaint |
| DELETE | /complaints/{id} | Delete complaint |

## Success Cases

### POST /complaints

Returns HTTP 200/201 with the created complaint.

### GET /complaints

Returns HTTP 200 with a list of complaints.

### GET /complaints/{id}

Returns HTTP 200 with the requested complaint.

### PUT /complaints/{id}

Returns HTTP 200 with the updated complaint.

### DELETE /complaints/{id}

Returns HTTP 200 after successful deletion.

## Error Cases

### Invalid complaint data

Returns HTTP 422 when required fields are missing or have invalid values.

### Complaint not found

Returns HTTP 404 when the requested complaint ID does not exist.

### Student not found

Returns HTTP 404 when a complaint is created for a non-existent student.

### Invalid endpoint

Returns HTTP 404 when an unknown endpoint is requested.