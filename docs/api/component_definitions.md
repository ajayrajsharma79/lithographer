# API Documentation: Component Definitions

This section describes the API endpoint for retrieving information about defined reusable front-end components. These definitions are typically managed by Administrators via the Admin UI.

**Authentication:** Requires authentication (CMS User Session or API Key).

---

## List Component Definitions

*   **Endpoint:** `GET /api/v1/component-definitions/`
*   **Description:** Retrieves a list of all available component definitions, including their configurable fields. This is useful for front-end applications or tools that need to know about available components.
*   **Authentication:** Required (`IsAuthenticated`).
*   **Query Parameters:**
    *   `page` (integer, optional): Page number for pagination.
    *   `search` (string, optional): Search by component name, api_id, or description.
*   **Response (Success):** `200 OK`
    ```json
    {
      "count": 3,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": "component-def-uuid-1",
          "name": "Hero Banner",
          "api_id": "hero_banner",
          "description": "A large banner typically used at the top of a page.",
          "icon": "fas fa-image", // Example icon class
          "field_definitions": [
            {
              "id": "comp-field-uuid-1",
              "name": "Headline",
              "api_id": "headline",
              "field_type": "text",
              "order": 0,
              "config": {"required": true, "help_text": "Main heading"}
            },
            {
              "id": "comp-field-uuid-2",
              "name": "Background Image",
              "api_id": "background_image",
              "field_type": "media", // Links to Media Library
              "order": 1,
              "config": {"allowed_media_types": ["image"]}
            }
            // ... other fields for this component
          ]
        },
        {
          "id": "component-def-uuid-2",
          "name": "Call To Action",
          "api_id": "cta_button",
          "description": "A button with text and a link.",
          "icon": null,
          "field_definitions": [
            // ... fields for CTA
          ]
        }
        // ... more component definitions
      ]
    }
    ```
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`.

---

## Retrieve Single Component Definition

*   **Endpoint:** `GET /api/v1/component-definitions/{api_id}/`
*   **Description:** Retrieves details for a specific component definition.
*   **Authentication:** Required (`IsAuthenticated`).
*   **URL Parameters:**
    *   `api_id` (string, required): The unique API ID of the `ComponentDefinition`.
*   **Response (Success):** `200 OK`
    *   Returns a single `ComponentDefinition` object (structure same as list response item).
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---