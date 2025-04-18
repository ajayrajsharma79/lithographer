# Lithographer CMS API Documentation

## Introduction

Welcome to the API documentation for the Lithographer CMS Framework. This API allows developers and external systems to interact with the CMS programmatically for tasks such as content delivery, content ingestion, media management, user authentication, and comment submission.

The API follows RESTful principles and primarily uses JSON for request and response bodies.

## Base URL

All API endpoints described in this documentation are relative to the following base URL:

```
/api/
```

For example, the endpoint for listing content types is `/api/v1/content-types/`. The full URL would depend on your deployment (e.g., `http://localhost:8000/api/v1/content-types/` during local development).

## Authentication

The Lithographer API uses different authentication methods depending on the endpoint and the type of user/system interacting with it:

1.  **API Keys (for External Systems/CMS Actions):**
    *   Used primarily for administrative actions or content ingestion by trusted external systems (e.g., AI agents, migration scripts).
    *   Keys are associated with a specific `CMSUser` account and inherit its permissions.
    *   Generate keys via the Admin UI (`Users` > `API Keys`).
    *   Include the key in the `Authorization` header of your request:
        ```
        Authorization: ApiKey <your_generated_api_key>
        ```

2.  **JWT Tokens (for Front-End Users):**
    *   Used for actions performed by authenticated front-end users (e.g., submitting comments, managing their profile).
    *   Obtain tokens via the `/api/auth/login/` endpoint using email and password. This returns an `access` token (short-lived) and a `refresh` token (longer-lived).
    *   Include the access token in the `Authorization` header as a Bearer token:
        ```
        Authorization: Bearer <your_access_token>
        ```
    *   Use the refresh token with the `/api/auth/token/refresh/` endpoint to obtain a new access token when the current one expires.

3.  **Session Authentication (for Browsable API/Admin):**
    *   Standard Django session authentication is supported, primarily for using the Browsable API interface in a web browser after logging into the Django Admin.

## Multilingual Support

Lithographer supports multilingual content.

*   **Requesting Specific Language:** For content delivery endpoints (e.g., fetching `ContentInstance` details), use the `lang` query parameter to specify the desired language code (e.g., `?lang=fr`, `?lang=en-GB`).
*   **Fallback Logic:** If content for the exact requested locale is not available, the API follows this fallback order:
    1.  Requested Locale (e.g., `en-gb`)
    2.  Base Language of Requested Locale (e.g., `en`)
    3.  Site Default Language (from System Settings, e.g., `fr`)
    4.  Base Language of Site Default (e.g., `fr` - only if different from #3)
    5.  First available translation for the field.
*   **Response Format:** Localized fields in API responses are typically returned as an object containing the `value` and the `language` code from which the value was retrieved (e.g., `"title": {"value": "Bonjour", "language": "fr"}`). Non-localizable fields are returned directly.
*   **Content Ingestion:** When submitting content via the API, provide translations for localizable fields as nested objects keyed by language code (see `content_ingestion.md`).

## Pagination

List endpoints (e.g., `/api/v1/content-instances/`, `/api/v1/media/assets/`) use page number pagination.

*   Use `?page=<number>` to request a specific page.
*   The number of items per page is determined by the `PAGE_SIZE` setting (default: 20).
*   The response includes `count` (total items), `next` (URL for the next page or null), and `previous` (URL for the previous page or null) fields alongside the `results` list.

## Common Response Formats

*   **Success (2xx):**
    *   `200 OK`: Standard success for `GET`, `PUT`, `PATCH`. Body contains requested data or updated resource representation.
    *   `201 Created`: Standard success for `POST` that creates a resource. Body usually contains the representation of the newly created resource.
    *   `204 No Content`: Standard success for `DELETE` or actions that don't return content. No response body.
*   **Client Errors (4xx):**
    *   `400 Bad Request`: Invalid request data (e.g., missing required fields, invalid format). Response body usually contains details about the validation errors.
    *   `401 Unauthorized`: Authentication credentials were not provided or are invalid.
    *   `403 Forbidden`: Authentication succeeded, but the user does not have permission to perform the action.
    *   `404 Not Found`: The requested resource does not exist.
*   **Server Errors (5xx):**
    *   `500 Internal Server Error`: An unexpected error occurred on the server.

Error responses typically follow the DRF standard format:
```json
{
    "detail": "Error message explaining the issue.",
    "field_errors": { // Optional: Only for validation errors (400)
        "field_name": ["Error message specific to this field."]
    }
}
```

## API Sections

*   [Authentication](./authentication.md) (Front-End Users)
*   [Content Delivery](./content_delivery.md)
*   [Content Ingestion](./content_ingestion.md)
*   [Media Library](./media.md)
*   [Comments](./comments.md)
*   [Webhooks (Receiving)](./webhooks.md)
*   [Component Definitions](./component_definitions.md)
*   [Taxonomies](./taxonomies.md)
*   [Admin/CMS Management](./admin.md) (Roles, CMS Users, etc.)