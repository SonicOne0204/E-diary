# E-Diary

An electronic diary web application API to manage students, teachers, subjects, attendance, grades, and invitations. Built with FastAPI and PostgreSQL, containerized with Docker.

---

## Features

* User management (students, teachers, principals)
* School creation and management
* Subject creation and management
* Attendance marking and tracking
* Grade recording and retrieval
* Teacher invitations and user authentication
* RESTful API design with validation
* Dockerized for easy deployment

---

## Technologies Used

* Python 3.10+
* FastAPI
* SQLAlchemy (ORM)
* PostgreSQL
* Docker & Docker Compose
* Pydantic (data validation)

---

## Getting Started

### Prerequisites

* Docker and Docker Compose installed
* Git installed

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/e-diary.git
cd e-diary
```

2. Build and start the containers:

```bash
docker-compose up --build
```

3. Create an admin user (inside the running container):

```bash
docker exec -it e-diary-backend python scripts/create_admin.py
```

4. The API will be available at:

```
http://localhost:8000
```

5. Visit the automatic API docs:

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Usage

* Use REST endpoints to manage schools, students, teachers, subjects, attendance, and grades.
* Example: Create a school

```JSON
POST /schools
{
  "name": "Springfield High School",
  "short_name": "SHS",
  "country": "United States of America",
  "address": "742 Evergreen Terrace"
}
```

---
s
## Testing

* Run tests using pytest:

```bash
pytest
```




