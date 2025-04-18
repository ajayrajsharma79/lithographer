# Getting Started with Lithographer CMS

This guide covers the initial setup and basic usage of the Lithographer CMS Admin interface.

## 1. Initial Project Setup

Follow these steps to set up the project locally for development:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd lithographer
    ```

2.  **Create Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # On Linux/macOS
    # or .\.venv\Scripts\activate # On Windows
    ```

3.  **Install Dependencies:**
    Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    *   Copy the example environment file: `cp .env.example .env` (Assuming `.env.example` exists, otherwise create `.env` manually).
    *   Edit the `.env` file and update the following variables for your local setup:
        *   `SECRET_KEY`: Generate a new secret key.
        *   `DATABASE_URL`: Set the connection string for your PostgreSQL database (e.g., `postgres://user:password@localhost:5432/lithographer_db`). Ensure the database exists and the user has permissions.
        *   `REDIS_URL`: Set the connection string for your Redis instance (used for caching and Celery).
        *   Update other settings like `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` if needed.

5.  **Run Database Migrations:**
    Apply the initial database schema.
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser:**
    Create the initial administrator account for the CMS.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set the email, password, and other required fields for the admin user.

7.  **Run Development Server:**
    Start the Django development server.
    ```bash
    python manage.py runserver
    ```
    The server will typically be available at `http://127.0.0.1:8000/`.

## 2. Logging In

1.  Open your web browser and navigate to the admin interface, usually `http://127.0.0.1:8000/admin/`.
2.  Enter the email address and password you created for the superuser (or other CMS User accounts).
3.  Click "Log in".

Once logged in, you can proceed to configure the system and manage content as described in the main README documentation.