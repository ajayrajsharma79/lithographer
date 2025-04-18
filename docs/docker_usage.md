# Using Docker for Lithographer Development and Deployment

This guide explains how to use the provided `Dockerfile` and `docker-compose.yml` to build and run the Lithographer CMS application stack using Docker.

## Prerequisites

*   **Docker:** Install Docker Desktop (for Mac/Windows) or Docker Engine (for Linux). [Get Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose:** Docker Compose is included with Docker Desktop. For Linux, you might need to install it separately. [Install Docker Compose](https://docs.docker.com/compose/install/)

## Overview

*   **`Dockerfile`:** Defines the steps to build a Docker image containing the Lithographer Django application, its Python dependencies, and necessary system libraries. It uses a multi-stage build for optimization.
*   **`.dockerignore`:** Lists files and directories that should be excluded from the Docker build context. This speeds up builds and reduces the final image size.
*   **`docker-compose.yml`:** Defines the multi-container application stack, including:
    *   `web`: The Lithographer Django application running with Gunicorn.
    *   `worker`: The Celery background worker.
    *   `db`: The PostgreSQL database.
    *   `redis`: The Redis instance (used for caching and Celery).
    *   *(Optional) `search`*: An Elasticsearch instance.
    It orchestrates the building of images (using the `Dockerfile`), creation of networks, management of volumes, and running of the services.
*   **`.env` file (You need to create this):** Stores environment-specific configuration and secrets (like database passwords, Django secret key, etc.) that are loaded by Docker Compose into the services. **This file should NOT be committed to version control.**

## Setup and Usage

1.  **Create the `.env` File:**
    *   In the project root directory (the same directory as `docker-compose.yml`), create a file named `.env`.
    *   Copy the example structure provided in the comments at the bottom of `docker-compose.yml` into your `.env` file.
    *   **Crucially, update the placeholder values:**
        *   Set a strong, unique `SECRET_KEY`. You can generate one using Django's utilities or online tools.
        *   Set a secure `POSTGRES_PASSWORD`.
        *   Adjust `DEBUG` (set to `False` for production).
        *   Configure `ALLOWED_HOSTS` (use `localhost,127.0.0.1` for local development; add your domain(s) for production).
        *   Configure any other necessary settings (Email, Elasticsearch URL if used, etc.).

    *Example minimal `.env` for local development:*
    ```env
    # General Django Settings
    SECRET_KEY=replace-this-with-a-strong-random-secret-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # PostgreSQL Database Configuration
    POSTGRES_DB=lithographer_db
    POSTGRES_USER=lithographer_user
    POSTGRES_PASSWORD=lithographer_pass # Use a stronger password!
    DATABASE_URL=postgres://lithographer_user:lithographer_pass@db:5432/lithographer_db

    # Redis Configuration
    REDIS_URL=redis://redis:6379/0

    # Celery Configuration
    CELERY_BROKER_URL=redis://redis:6379/1
    CELERY_RESULT_BACKEND=redis://redis:6379/2
    ```

2.  **Build and Run the Services:**
    *   Open a terminal in the project root directory.
    *   Run the following command:
        ```bash
        docker-compose up --build
        ```
        *   `docker-compose up`: Starts all the services defined in `docker-compose.yml`.
        *   `--build`: Forces Docker Compose to build the image for the `web` and `worker` services using the `Dockerfile` before starting the containers. You only need `--build` the first time or when you change the `Dockerfile` or `requirements.txt`. For subsequent starts, `docker-compose up` is sufficient.
    *   Docker Compose will download the base images (Postgres, Redis), build your application image, create the network and volumes, and start all the containers.
    *   You will see logs from all the services interleaved in your terminal. Wait until you see messages indicating the database is ready and the web server (Gunicorn) has started.

3.  **Apply Database Migrations (First time setup):**
    *   While the services are running (from `docker-compose up`), open a *second* terminal in the project root directory.
    *   Run the migrations using `docker-compose exec`:
        ```bash
        docker-compose exec web python manage.py migrate
        ```
        *   `docker-compose exec web`: Executes a command inside the running `web` service container.

4.  **Create a Superuser (First time setup):**
    *   In the second terminal, create an admin user:
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
    *   Follow the prompts to set the username, email, and password.

5.  **Access the Application:**
    *   Open your web browser and navigate to `http://localhost:8000` (or `http://127.0.0.1:8000`).
    *   You should see the Lithographer application (or a Django welcome/error page if the frontend isn't fully set up).
    *   Access the Django admin interface at `http://localhost:8000/admin/` and log in with the superuser credentials you created.

6.  **Running Other Management Commands:**
    *   Use `docker-compose exec web python manage.py <your_command>` to run any other Django management commands (e.g., `collectstatic`, `shell`).

7.  **Stopping the Services:**
    *   Go back to the first terminal where `docker-compose up` is running.
    *   Press `Ctrl + C` to stop the services.
    *   Alternatively, from the second terminal, run:
        ```bash
        docker-compose down
        ```
        *   `docker-compose down`: Stops and removes the containers, network, and potentially volumes (use `docker-compose down -v` to also remove named volumes like the database data - use with caution!).

## Development vs. Production

*   **Development:** The `docker-compose.yml` includes commented-out volume mounts (`- .:/app`) for the `web` and `worker` services. Uncommenting these lines mounts your local project directory directly into the containers. This allows you to see code changes immediately without rebuilding the image (though you might need to restart the Gunicorn/Celery process depending on your setup).
*   **Production:** For production, you should **not** mount the source code directly. Rely on the image built by the `Dockerfile`. The application code is copied into the image during the build process. You would typically build the image once and deploy that immutable image. Static and media files should be handled via volumes or external storage solutions. Ensure `DEBUG=False` in your `.env` file for production.

## Troubleshooting

*   **Port Conflicts:** If `localhost:8000` is already in use on your host machine, change the host port mapping in `docker-compose.yml` (e.g., `"8001:8000"`) and access the app at `http://localhost:8001`.
*   **`.env` File Errors:** Ensure the `.env` file exists, is correctly formatted, and contains all necessary variables referenced in `docker-compose.yml` and your Django settings.
*   **Build Errors:** Check the output during the `docker-compose up --build` step for errors related to system dependencies, Python packages (`requirements.txt`), or Dockerfile syntax.
*   **Database Connection Errors:** Verify the `DATABASE_URL` in your `.env` file matches the service name (`db`), user, password, and database name defined for the `db` service. Ensure the `db` container is running and healthy (`docker-compose ps`).
*   **Permissions:** If you encounter permission errors related to file access (especially with mounted volumes), check the user/group ownership inside the container (`USER django-user` in the Dockerfile) and potentially adjust permissions on the host or volume mounts.