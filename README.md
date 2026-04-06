CodeCraftHub
A beginner-friendly, light-weight REST API project built with Flask that lets developers track courses they want to learn. Data is stored in a simple JSON file (no database). This project focuses on learning REST API basics: creating, reading, updating, and deleting courses via HTTP endpoints.

1) Project overview and description
CodeCraftHub is a small learning project showing how to build a RESTful API with Flask and persist data without a database. Each course record includes:

id: auto-generated, starting from 1
name: required
description: required
target_date: required, format YYYY-MM-DD
status: required, one of "Not Started", "In Progress", or "Completed"
created_at: auto-generated timestamp
All data is stored in a JSON file named
courses.json
inside a
data/
directory. The app creates the file automatically if it doesn’t exist yet.

2) Features
Create, read, update, and delete (CRUD) courses
Auto-generated IDs (start at 1)
Validation for required fields and allowed statuses
Target date validation (YYYY-MM-DD)
Auto-generated created_at timestamp
All data stored in a single JSON file (courses.json)
Simple, beginner-friendly codebase and endpoints
3) Installation instructions (step-by-step)
Prerequisites:

Python 3.x (tested with Python 3.8+)
Internet access (to install Flask)
Steps:

Create and activate a virtual environment (recommended)
On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
On Windows:
python -m venv venv
venv\Scripts\activate
Install Flask
pip install Flask
Set up the project files
Create a project folder, e.g., CodeCraftHub
Inside CodeCraftHub, add a file named app.py (the complete code is provided in the project)
Create a subfolder named data
The app will automatically create data/courses.json on first run if it doesn’t exist
Optional:

You can add a requirements.txt with:
Flask==2.x
(If you’re using a virtual environment, you can run: pip install -r requirements.txt)
(Optional) Seed an empty data file
You can manually create data/courses.json with an empty array: []
4) How to run the application
Ensure you are in the project directory (where app.py resides).

Run the Flask development server:

python app.py
Open in your browser or use curl:
Base URL: http://127.0.0.1:5000
API base: /api/courses
The app will automatically create data/courses.json on first run if it doesn’t exist.

5) API endpoints documentation (with examples)
All endpoints start with /api/courses

Note: The primary endpoints are designed for CRUD operations. Some operations support additional ways to specify the target course (e.g., via path parameter or via request body).

POST /api/courses

Purpose: Add a new course
Request body (JSON): { "name": "Python Basics", "description": "Learn Python syntax and basics.", "target_date": "2026-05-15", "status": "Not Started" }
Response: 201 Created with the created course object
Example:
curl -X POST -H "Content-Type: application/json" -d '{"name":"Python Basics","description":"Learn Python syntax and basics.","target_date":"2026-05-15","status":"Not Started"}' http://127.0.0.1:5000/api/courses
Possible errors:
400 Missing required fields or invalid data
500 Storage write error
GET /api/courses

Purpose: Get all courses
Response: 200 OK with an array of course objects
Example:
curl http://127.0.0.1:5000/api/courses
Optional: You can fetch a single course by ID via query param
curl http://127.0.0.1:5000/api/courses?id=1
Note: For clarity, the path /api/courses/<id> also exists:
GET /api/courses/1
Response: 200 OK with the course object or 404 if not found
GET /api/courses/int:course_id

Purpose: Get a specific course by ID
Response: 200 OK with the course object, or 404 if not found
Example:
curl http://127.0.0.1:5000/api/courses/1
PUT /api/courses/int:course_id

Purpose: Update a course by ID (partial updates allowed)
Request body (JSON) (any subset; e.g.): { "name": "Python Basics Updated", "description": "Updated description", "target_date": "2026-06-01", "status": "In Progress" }
Response: 200 OK with the updated course
Example:
curl -X PUT -H "Content-Type: application/json" -d '{"status":"In Progress"}' http://127.0.0.1:5000/api/courses/1
PUT /api/courses

Purpose: Update a course by providing an id in the request body (alternative)
Request body (JSON) must include: { "id": 1, "name": "..." // other fields to update }
Response: 200 OK with the updated course
Example:
curl -X PUT -H "Content-Type: application/json" -d '{"id":1,"status":"Completed"}' http://127.0.0.1:5000/api/courses
DELETE /api/courses/int:course_id

Purpose: Delete a course by ID
Response: 204 No Content on success, or 404 if not found
Example:
curl -X DELETE http://127.0.0.1:5000/api/courses/1
DELETE /api/courses

Purpose: Delete a course by ID provided in the body or as a query parameter
Request body example: { "id": 1 }
Or query string example:
/api/courses?id=1
Response: 204 No Content on success, or 404 if not found
Validation and error messages you may see:

400 Missing required fields or invalid data
404 Course not found
500 File read/write errors
Important data validation rules (enforced in code):

name: required, non-empty string
description: required, non-empty string
target_date: required, format YYYY-MM-DD
status: required, one of "Not Started", "In Progress", "Completed"
created_at: auto-generated on creation
6) Testing instructions
Manual testing with curl (examples):

Create a course

curl -X POST -H "Content-Type: application/json"
-d '{"name":"Intro to Flask","description":"Learn to build APIs with Flask.","target_date":"2026-04-30","status":"Not Started"}'
http://127.0.0.1:5000/api/courses
Get all courses

curl http://127.0.0.1:5000/api/courses
Get a specific course

curl http://127.0.0.1:5000/api/courses/1
Update a course by ID

curl -X PUT -H "Content-Type: application/json"
-d '{"status":"In Progress"}'
http://127.0.0.1:5000/api/courses/1
Delete a course by ID

curl -X DELETE http://127.0.0.1:5000/api/courses/1
Tips:

Use a REST client like Postman or Insomnia for a more visual testing experience.
Validate responses by checking HTTP status codes and the returned JSON.
7) Troubleshooting common issues
Server won’t start or port already in use

Make sure no other process is using port 5000. Try another port by setting an environment variable or editing the code to run on a different port.
Data file not created or unreadable

Ensure the app has permission to create the data/ directory. The app will auto-create data/courses.json on first run.
Validation errors (e.g., invalid date or status)

Double-check the format:
target_date must be YYYY-MM-DD (e.g., 2026-05-15)
status must be one of "Not Started", "In Progress", or "Completed"
JSON parse errors in courses.json

If you manually edit the file and introduce invalid JSON, the app will attempt to recover by treating the data as an empty list. For safety, always validate JSON (e.g., using a JSON validator) and keep the file well-formed.
File read/write errors

Check file permissions for data/courses.json and the data/ directory. Ensure the user running the Flask app can read and write these files.
8) Project structure explanation
app.py

The main Flask application that exposes all REST API endpoints under /api/courses
Contains all CRUD logic, input validation, and JSON file storage integration
Includes helper functions for loading/saving data and validating input
data/

This directory holds the storage file for course data
courses.json is auto-created by the app if missing
requirements.txt (optional)

A place to list dependencies like Flask for easy setup
Example content:
Flask==2.x
Other notes

The data model is intentionally simple to help beginners understand how REST APIs work without a database.
All data is stored in a single JSON file, which is easy to inspect and modify manually if desired.
