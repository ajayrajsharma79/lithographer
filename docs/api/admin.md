# API Documentation: Admin / CMS Management

This section covers API endpoints related to managing CMS-specific resources like CMS Users and Roles. These endpoints are typically restricted to users with Administrator privileges.

**Authentication:** Requires authentication (CMS User Session or API Key) with appropriate Administrator permissions.

---

## List CMS Users

*   **Endpoint:** `GET /api/v1/cms-users/`
*   **Description:** Retrieves a paginated list of CMS users (administrators, editors, etc.).
*   **Permissions:** Admin users.
*   **Response:** Standard paginated list containing CMSUser objects (see `CMSUserSerializer` for fields, excluding password).

---

## Retrieve/Update/Delete CMS User

*   **Endpoints:**
    *   `GET /api/v1/cms-users/{user_pk}/`
    *   `PUT /api/v1/cms-users/{user_pk}/`
    *   `PATCH /api/v1/cms-users/{user_pk}/`
    *   `DELETE /api/v1/cms-users/{user_pk}/`
*   **Description:** Standard CRUD operations for CMS users.
*   **Permissions:** Admin users.
*   **Request/Response:** See `CMSUserSerializer`. Password changes require the `password` field in the request body.

---

## List Roles

*   **Endpoint:** `GET /api/v1/roles/`
*   **Description:** Retrieves a list of defined CMS user roles.
*   **Permissions:** Admin users.
*   **Response:** List containing Role objects, including the `permissions` list (JSON field).

---

## Retrieve/Update/Delete Role

*   **Endpoints:**
    *   `GET /api/v1/roles/{role_pk}/`
    *   `POST /api/v1/roles/`
    *   `PUT /api/v1/roles/{role_pk}/`
    *   `PATCH /api/v1/roles/{role_pk}/`
    *   `DELETE /api/v1/roles/{role_pk}/`
*   **Description:** Standard CRUD operations for CMS roles. Allows creating custom roles and assigning permission strings via the `permissions` JSON field. System roles cannot be deleted.
*   **Permissions:** Admin users.
*   **Request/Response:** See `RoleSerializer`.

---

## Manage API Keys

API Keys are managed via the `/api/v1/api-keys/` endpoint (standard ModelViewSet).

*   **Permissions:** Authenticated CMS users can list/create/delete their *own* keys. Admin users can manage *all* keys.
*   See `APIKeySerializer` for request/response details. The actual key is only returned on creation.

---