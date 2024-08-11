
# FormFlow Project

## Overview

FormFlow is a Django-based application designed to create, manage, and process surveys and forms. The application allows users to create customizable forms with various types of questions, collect responses, and analyze the results.

## Table of Contents

1. [Features](#features)
2. [Technologies](#technologies)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Environment Variables](#environment-variables)
6. [Running the Project](#running-the-project)
7. [Testing](#testing)
8. [API Endpoints](#api-endpoints)
9. [Contribution Guidelines](#contribution-guidelines)
10. [License](#license)

## Features

- **User Authentication:** Secure user authentication and authorization using Django's built-in features.
- **Form Creation:** Allows users to create forms with different types of questions, including text, rating, multiple-choice, and matrix.
- **Response Management:** Users can submit responses to forms, which are validated based on the type of questions.
- **API Integration:** RESTful API for creating, retrieving, updating, and deleting forms, questions, and responses.
- **Status Tracking:** Track the status of forms and responses (Draft, Published, Archived).

## Technologies

- **Python 3.10**
- **Django 4.x**
- **Django REST Framework**
- **PostgreSQL** (or your preferred database)
- **Docker** (for containerization)
- **Git** (for version control)

## Project Structure

```
FormFlow/
├── core/
│   ├── models.py          # Core models used across the project
│   ├── views.py           # Base views for common functionality
│   └── ...
├── survey/
│   ├── models.py          # Models specific to survey and form handling
│   ├── serializers.py     # DRF serializers for survey models
│   ├── views.py           # ViewSets for handling API requests
│   ├── urls.py            # URL routing for the survey app
│   └── tests.py           # Unit tests for survey functionalities
├── authentication/
│   ├── models.py          # Custom user models and authentication handling
│   ├── serializers.py     # DRF serializers for authentication
│   ├── views.py           # Views for login, signup, etc.
│   └── urls.py            # URL routing for authentication
├── FormFlow/
│   ├── settings.py        # Django settings
│   ├── urls.py            # Project-wide URL configuration
│   ├── wsgi.py            # WSGI entry point for deployment
│   └── ...
├── manage.py              # Django management script
└── README.md              # Project README file
```

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL (or any other database you're using)
- Docker (optional but recommended for containerization)
- Git

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/FormFlow.git
   cd FormFlow
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install poetry
   poetry install
   ```

4. **Set Up the Database:**

   Ensure PostgreSQL is running and create a new database for the project.

   ```bash
   ./scripts/local-remigrate.sh
   ```

   Update the `DATABASES` setting in `settings.py` with your database credentials.

5. **Run Migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser:**

   ```bash
   python shell.py createsuperuser "username" "password"
   ```

## Environment Variables

Create a `.env` file in the root directory and add the following environment variables:

```
SECRET_KEY=your_secret_key_here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/formflow_db
```

Create a `FormFlow/local_settings.py` file in the root directory and add the following environment variables:

```
DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

```

## Running the Project

1. **Start the Development Server:**

   ```bash
   python manage.py runserver
   ```

2. **Access the Admin Panel:**

   Visit `http://127.0.0.1:8000/admin` and log in with your superuser credentials.

## Testing

To run the unit tests:

```bash
python manage.py test
```

The tests are located in the `survey/tests.py` file and cover various scenarios for the Response and Answer models.

## API Endpoints

- **Swagger:**
  - `GET /swagger/`: List all api's.

- **redoc:**
  - `GET /redoc/`: List all api's.

- **admin:**
  - `GET /admin/`: admin panel.



[//]: # (- **Forms:**)

[//]: # (  - `GET /api/forms/`: List all forms.)

[//]: # (  - `POST /api/forms/`: Create a new form.)

[//]: # (  - `GET /api/forms/{id}/`: Retrieve a specific form.)

[//]: # (  - `PUT /api/forms/{id}/`: Update a specific form.)

[//]: # ()
[//]: # ([//]: # &#40;  - `DELETE /api/forms/{id}/`: Delete a specific form.&#41;)
[//]: # ()
[//]: # (- **Responses:**)

[//]: # (  - `GET /api/responses/`: List all responses.)

[//]: # (  - `POST /api/responses/`: Create a new response with answers.)

[//]: # (  - `GET /api/responses/{id}/`: Retrieve a specific response.)

[//]: # (  - `PUT /api/responses/{id}/`: Update a specific response.)

[//]: # ()
[//]: # ([//]: # &#40;  - `DELETE /api/responses/{id}/`: Delete a specific response.&#41;)

## Contribution Guidelines

If you wish to contribute to this project:

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch to your forked repository.
5. Create a Pull Request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
