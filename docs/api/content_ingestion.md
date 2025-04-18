# API Documentation: Content Ingestion

This section describes the API endpoint used to programmatically create new content instances within the CMS. This is typically used by external systems, scripts, or integrations.

**Authentication:** Requires API Key authentication. The key must be associated with a `CMSUser` that has the necessary permissions (e.g., `content.add_contentinstance`).

---

## Create Content Instance

*   **Endpoint:** `POST /api/v1/content-instances/`
*   **Description:** Creates a new content instance based on a specified content type and provided field data.
*   **Authentication:** API Key required (`Authorization: ApiKey <your_api_key>`).
*   **Permissions:** Requires `content.add_contentinstance` permission (or equivalent role).
*   **Request Body:** `application/json`
    ```json
    {
      "content_type": "blog-post", // Required: api_id or UUID of the ContentType
      "status": "draft",           // Optional: Initial status (defaults usually to 'draft')
      "term_ids": [                // Optional: List of UUIDs for associated Taxonomy Terms
        "term-uuid-1",
        "term-uuid-2"
      ],
      "content_data": {            // Required: Object containing field data
        "title": {                 // Example: Localizable 'text' field
          "en": "My API Ingested Post",
          "fr": "Mon Article ingéré par API"
        },
        "slug": "my-api-ingested-post", // Example: Non-localizable 'text' field
        "publish_date": "2025-04-18T10:00:00Z", // Example: 'date' field (ISO 8601)
        "is_featured": true,       // Example: 'boolean' field
        "main_body": {             // Example: Localizable 'rich_text' field
          "en": "<p>This is the English body.</p>",
          "fr": "<p>Ceci est le corps français.</p>"
        },
        "featured_image": "media-asset-uuid-123", // Example: 'media' field (provide MediaAsset UUID)
        "author_ref": "content-instance-uuid-abc" // Example: 'relationship' field (provide ContentInstance UUID)
        // ... other fields based on ContentType definition
      }
    }
    ```
    *   `content_type` (string, required): The `api_id` or UUID of the `ContentType` definition to use.
    *   `status` (string, optional): The initial status for the content instance (e.g., `draft`, `published`). Defaults to the system default if not provided. Permissions might restrict setting certain statuses directly.
    *   `term_ids` (array[uuid], optional): A list of UUIDs corresponding to `Term` objects to associate with this content instance.
    *   `content_data` (object, required): An object where keys are the `api_id` of the `FieldDefinition`s for the specified `content_type`.
        *   **Non-Localizable Fields:** The value is the direct data for the field (string, number, boolean, UUID for relationships/media).
        *   **Localizable Fields:** The value is an object where keys are language codes (e.g., `en`, `fr`) and values are the translated data for that language. Provide data only for the necessary languages.
*   **Response (Success):** `201 Created`
    *   Returns the full representation of the newly created `ContentInstance`, including its generated ID, status, and structured `content_data` (with language fallbacks applied based on default settings). See the [Content Delivery](./content_delivery.md#retrieve-single-content-instance) documentation for the response structure.
*   **Response (Error):**
    *   `400 Bad Request`: Invalid data (e.g., missing required fields in `content_data`, incorrect data types, invalid `content_type` or `term_ids`, validation errors based on field definitions).
    *   `401 Unauthorized`: Missing or invalid API Key.
    *   `403 Forbidden`: API Key is valid, but the associated user lacks permission.
    *   `404 Not Found`: Specified `ContentType` or `Term` UUIDs do not exist.

---