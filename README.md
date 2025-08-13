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

2. Create your `.env` file from the example:

```bash
cp .env.example .env
```

Then edit `.env` and set your own values (database credentials, secret key, etc.).

3. Build and start the containers:

```bash
docker-compose up --build
```

4. Create an admin user (inside the running container):

```bash
docker exec backend python -m app.scripts.create_admin
```

5. The API will be available at:

```
http://localhost:8000
```

6. Visit the automatic API docs:

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Usage

* Use REST endpoints to manage schools, students, teachers, subjects, attendance, and grades.
* Example: Create a school

```json
POST /schools
{
  "name": "Springfield High School",
  "short_name": "SHS",
  "country": "United States of America",
  "address": "742 Evergreen Terrace"
}
```

---

## Testing

* Run tests using pytest:

```bash
pytest
```

