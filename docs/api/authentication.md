# API Documentation: Front-End User Authentication

This section details the API endpoints for managing front-end user accounts, including registration, login (using JWT), and profile management.

**Authentication:** Most endpoints require JWT Bearer token authentication after login, except for registration and login itself.

---

## Register New User

*   **Endpoint:** `POST /api/auth/register/`
*   **Description:** Creates a new front-end user account. Email verification might be required depending on configuration (currently not implemented).
*   **Authentication:** None required.
*   **Permissions:** AllowAny.
*   **Request Body:** `application/json`
    ```json
    {
      "email": "user@example.com",
      "username": "newuser",
      "password": "YourStrongPassword123!",
      "password2": "YourStrongPassword123!",
      "display_name": "New User Display", // Optional, defaults to username
      "first_name": "New",               // Optional
      "last_name": "User"                // Optional
    }
    ```
    *   `email` (string, required): Unique email address.
    *   `username` (string, required): Unique username.
    *   `password` (string, required): User's chosen password. Must meet complexity requirements if configured.
    *   `password2` (string, required): Confirmation of the password. Must match `password`.
    *   `display_name` (string, optional): Public display name. Defaults to `username` if omitted.
    *   `first_name` (string, optional): User's first name.
    *   `last_name` (string, optional): User's last name.
*   **Response (Success):** `201 Created`
    ```json
    {
      "id": "uuid-string-of-new-user",
      "email": "user@example.com",
      "username": "newuser",
      "first_name": "New",
      "last_name": "User",
      "display_name": "New User Display",
      "status": "active", // Or "inactive" if email verification is implemented
      "is_active": true, // Reflects Django's active flag
      "date_joined": "iso-8601-timestamp",
      "last_login": null
    }
    ```
*   **Response (Error):**
    *   `400 Bad Request`: If passwords don't match, email/username already exists, or other validation fails. Body contains error details.

---

## Login (Obtain JWT Tokens)

*   **Endpoint:** `POST /api/auth/login/`
*   **Description:** Authenticates a front-end user using email and password, returning JWT access and refresh tokens.
*   **Authentication:** None required.
*   **Permissions:** AllowAny.
*   **Request Body:** `application/json`
    ```json
    {
      "email": "user@example.com",
      "password": "userpassword"
    }
    ```
    *   `email` (string, required): User's registered email.
    *   `password` (string, required): User's password.
*   **Response (Success):** `200 OK`
    ```json
    {
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcyODQ1ODk3MywiaWF0IjoxNzI4MzcyNTczLCJqdGkiOiI3Zj...",
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4MzcyODczLCJpYXQiOjE3MjgzNzI1NzMsImp0aSI6IjNm..."
    }
    ```
    *   `refresh` (string): Refresh token (longer-lived).
    *   `access` (string): Access token (shorter-lived). Use this in `Authorization: Bearer <access_token>` header for subsequent requests.
*   **Response (Error):**
    *   `401 Unauthorized`: If credentials are invalid.

---

## Refresh JWT Access Token

*   **Endpoint:** `POST /api/auth/token/refresh/`
*   **Description:** Obtains a new JWT access token using a valid refresh token.
*   **Authentication:** None required (uses refresh token in body).
*   **Permissions:** AllowAny.
*   **Request Body:** `application/json`
    ```json
    {
      "refresh": "your_valid_refresh_token"
    }
    ```
*   **Response (Success):** `200 OK`
    ```json
    {
      "access": "new_access_token_string"
      // May optionally include a new refresh token if ROTATE_REFRESH_TOKENS is True
      // "refresh": "new_refresh_token_string"
    }
    ```
*   **Response (Error):**
    *   `401 Unauthorized`: If the refresh token is invalid or expired.

---

## Verify JWT Access Token

*   **Endpoint:** `POST /api/auth/token/verify/`
*   **Description:** Checks if an access token is valid (not expired, correct signature). Does not guarantee the user still exists or is active.
*   **Authentication:** None required (uses token in body).
*   **Permissions:** AllowAny.
*   **Request Body:** `application/json`
    ```json
    {
      "token": "your_access_token_to_verify"
    }
    ```
*   **Response (Success):** `200 OK` (Empty body)
*   **Response (Error):**
    *   `401 Unauthorized`: If the token is invalid.

---

## View/Update User Profile

*   **Endpoint:** `GET`, `PUT`, `PATCH /api/auth/profile/`
*   **Description:** Allows an authenticated front-end user to view or update their own profile information.
*   **Authentication:** JWT Bearer Token required (`Authorization: Bearer <access_token>`).
*   **Permissions:** IsAuthenticated (and must be a `FrontEndUser`).
*   **Request Body (`PUT`, `PATCH`):** `application/json`
    *   Provide fields to update. `PUT` requires all writable fields, `PATCH` allows partial updates.
    *   Cannot update `email` or `username` via this endpoint.
    ```json
    // Example PATCH request
    {
      "first_name": "UpdatedFirstName",
      "display_name": "UpdatedDisplayName"
    }
    ```
    *   `first_name` (string, optional)
    *   `last_name` (string, optional)
    *   `display_name` (string, optional)
    *   *(Other profile fields like bio, avatar URL if added)*
*   **Response (Success):** `200 OK`
    *   Returns the full profile data (excluding sensitive fields) after update.
    ```json
    {
      "id": "user-uuid",
      "email": "user@example.com", // Read-only
      "username": "currentuser",   // Read-only
      "first_name": "UpdatedFirstName",
      "last_name": "UserLastName",
      "display_name": "UpdatedDisplayName",
      "date_joined": "iso-8601-timestamp" // Read-only
    }
    ```
*   **Response (Error):**
    *   `400 Bad Request`: Invalid data format.
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: User does not have permission (e.g., trying to access as CMSUser).

---

## Password Reset

*(Endpoints not yet implemented)*

*   **Request Reset:** `POST /api/auth/password/reset/` (Requires email)
*   **Confirm Reset:** `POST /api/auth/password/reset/confirm/` (Requires uid, token, new passwords)

---