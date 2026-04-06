from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# --------- Configuration ---------
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'courses.json')
ALLOWED_STATUSES = {'Not Started', 'In Progress', 'Completed'}

# --------- Helper utilities ---------

def ensure_data_file():
    """Create data directory and courses.json if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

def load_courses():
    """Load and return the list of courses from the JSON file."""
    ensure_data_file()
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except (IOError, json.JSONDecodeError):
        # If there is a read error or bad JSON, start fresh
        return []

def save_courses(courses):
    """Persist the list of courses to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(courses, f, indent=2)
    except IOError as e:
        # Re-raise so callers can handle / respond appropriately
        raise e

def get_next_id(courses):
    """Return the next auto-incrementing ID starting from 1."""
    if not courses:
        return 1
    return max(c['id'] for c in courses) + 1

def find_course(courses, course_id):
    """Find and return a course by its ID, or None if not found."""
    for c in courses:
        if c.get('id') == course_id:
            return c
    return None

def is_valid_date(date_str):
    """Validate date string is in YYYY-MM-DD format."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def current_timestamp():
    """Return UTC timestamp in ISO format with Z suffix (e.g., 2024-08-12T12:34:56Z)."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# --------- Flask App ---------

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --------- Routes (CRUD) ---------

# Create a new course
@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400

    # Validate required fields
    required_fields = ['name', 'description', 'target_date', 'status']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    name = data['name']
    description = data['description']
    target_date = data['target_date']
    status = data['status']

    # Simple validations
    if not isinstance(name, str) or not name.strip():
        return jsonify({'error': 'Field "name" must be a non-empty string'}), 400
    if not isinstance(description, str) or not description.strip():
        return jsonify({'error': 'Field "description" must be a non-empty string'}), 400
    if not is_valid_date(target_date):
        return jsonify({'error': 'Field "target_date" must be in YYYY-MM-DD format'}), 400
    if status not in ALLOWED_STATUSES:
        return jsonify({'error': f'Field "status" must be one of {list(ALLOWED_STATUSES)}'}), 400

    # Create new course
    courses = load_courses()
    new_id = get_next_id(courses)
    course = {
        'id': new_id,
        'name': name.strip(),
        'description': description.strip(),
        'target_date': target_date,
        'status': status,
        'created_at': current_timestamp()
    }

    courses.append(course)
    try:
        save_courses(courses)
    except IOError:
        return jsonify({'error': 'Failed to write data to storage'}), 500

    return jsonify(course), 201

# Get all courses or a specific course via query parameter (e.g., /api/courses?id=1)
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = load_courses()

    # Optional: allow fetching a single course by ID via query param
    cid = request.args.get('id') or request.args.get('course_id')
    if cid:
        try:
            course_id = int(cid)
        except ValueError:
            return jsonify({'error': 'Query parameter "id" must be an integer'}), 400

        course = find_course(courses, course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        return jsonify(course), 200

    # Return all courses
    return jsonify(courses), 200

# Get a specific course by ID (path-based)
@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course_by_id(course_id):
    courses = load_courses()
    course = find_course(courses, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify(course), 200

# Get course statistics
@app.route('/api/courses/stats', methods=['GET'])
def get_course_stats():
    courses = load_courses()

    stats = {
        "total_courses": len(courses),
        "Not Started": 0,
        "In Progress": 0,
        "Completed": 0
    }

    for course in courses:
        status = course.get("status")
        if status in stats:
            stats[status] += 1

    return jsonify(stats), 200

# Update a course by ID in the URL path
@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course_by_id(course_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request must be JSON'}), 400

    courses = load_courses()
    course = find_course(courses, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Allow partial updates
    updated = False
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({'error': 'Field "name" must be a non-empty string'}), 400
        course['name'] = data['name'].strip()
        updated = True
    if 'description' in data:
        if not isinstance(data['description'], str) or not data['description'].strip():
            return jsonify({'error': 'Field "description" must be a non-empty string'}), 400
        course['description'] = data['description'].strip()
        updated = True
    if 'target_date' in data:
        if not is_valid_date(data['target_date']):
            return jsonify({'error': 'Field "target_date" must be in YYYY-MM-DD format'}), 400
        course['target_date'] = data['target_date']
        updated = True
    if 'status' in data:
        if data['status'] not in ALLOWED_STATUSES:
            return jsonify({'error': f'Field "status" must be one of {list(ALLOWED_STATUSES)}'}), 400
        course['status'] = data['status']
        updated = True

    if not updated:
        return jsonify({'error': 'No valid fields provided to update'}), 400

    try:
        save_courses(courses)
    except IOError:
        return jsonify({'error': 'Failed to write data to storage'}), 500

    return jsonify(course), 200

# Update a course by ID provided in body (alternative /api/courses route)
@app.route('/api/courses', methods=['PUT'])
def update_course_by_body():
    data = request.get_json(silent=True)
    if not data or 'id' not in data:
        return jsonify({'error': 'Request must include "id" field to identify the course'}), 400

    try:
        course_id = int(data['id'])
    except (ValueError, TypeError):
        return jsonify({'error': '"id" must be an integer'}), 400

    courses = load_courses()
    course = find_course(courses, course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    updated = False
    # Allow partial updates via body
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({'error': 'Field "name" must be a non-empty string'}), 400
        course['name'] = data['name'].strip()
        updated = True
    if 'description' in data:
        if not isinstance(data['description'], str) or not data['description'].strip():
            return jsonify({'error': 'Field "description" must be a non-empty string'}), 400
        course['description'] = data['description'].strip()
        updated = True
    if 'target_date' in data:
        if not is_valid_date(data['target_date']):
            return jsonify({'error': 'Field "target_date" must be in YYYY-MM-DD format'}), 400
        course['target_date'] = data['target_date']
        updated = True
    if 'status' in data:
        if data['status'] not in ALLOWED_STATUSES:
            return jsonify({'error': f'Field "status" must be one of {list(ALLOWED_STATUSES)}'}), 400
        course['status'] = data['status']
        updated = True

    if not updated:
        return jsonify({'error': 'No valid fields provided to update'}), 400

    try:
        save_courses(courses)
    except IOError:
        return jsonify({'error': 'Failed to write data to storage'}), 500

    return jsonify(course), 200

# Delete a course by ID in the URL path
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course_by_id(course_id):
    courses = load_courses()
    new_courses = [c for c in courses if c.get('id') != course_id]
    if len(new_courses) == len(courses):
        return jsonify({'error': 'Course not found'}), 404

    try:
        save_courses(new_courses)
    except IOError:
        return jsonify({'error': 'Failed to write data to storage'}), 500

    return '', 204

# Delete a course by ID provided in body or query (alternative /api/courses route)
@app.route('/api/courses', methods=['DELETE'])
def delete_course_by_body():
    # Try to get id from JSON body
    data = request.get_json(silent=True)
    course_id = None

    if data and 'id' in data:
        try:
            course_id = int(data['id'])
        except ValueError:
            return jsonify({'error': '"id" in body must be an integer'}), 400
    else:
        # Fallback to query string
        cid = request.args.get('id') or request.args.get('course_id')
        if cid:
            try:
                course_id = int(cid)
            except ValueError:
                return jsonify({'error': 'Query parameter "id" must be an integer'}), 400

    if course_id is None:
        return jsonify({'error': 'Please provide an "id" to delete (in body or as query param)'}), 400

    courses = load_courses()
    new_courses = [c for c in courses if c.get('id') != course_id]
    if len(new_courses) == len(courses):
        return jsonify({'error': 'Course not found'}), 404

    try:
        save_courses(new_courses)
    except IOError:
        return jsonify({'error': 'Failed to write data to storage'}), 500

    return '', 204

# --------- Run the app ---------

if __name__ == '__main__':
    # Ensure the data file exists on first run
    ensure_data_file()
    # Run the Flask development server
    app.run(debug=True)