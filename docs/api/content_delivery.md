# API Documentation: Content Delivery

This section describes the API endpoints used to retrieve content managed by the CMS. These endpoints are typically consumed by front-end applications or other services displaying the content.

**Authentication:** Generally read-only access, may not require authentication depending on permission setup (`IsAuthenticatedOrReadOnly` is the default). Specific content types might have stricter permissions.

---

## List Content Instances

*   **Endpoint:** `GET /api/v1/content-instances/`
*   **Description:** Retrieves a paginated list of content instances. Can be filtered by content type and other fields.
*   **Authentication:** Optional (Default: Read-only allowed).
*   **Query Parameters:**
    *   `page` (integer, optional): Page number for pagination.
    *   `content_type` (string, optional): Filter by the `api_id` of the `ContentType` (e.g., `?content_type=blog-post`).
    *   `lang` (string, optional): Specify the desired language code (e.g., `en`, `fr-ca`). See [Multilingual Support](#multilingual-support) in the main index for fallback logic.
    *   `status` (string, optional): Filter by content status (e.g., `?status=published`). Only 'published' is typically useful for delivery APIs.
    *   *(Other filtering options based on specific fields might be available via `django-filter`)*.
    *   `search` (string, optional): Perform a search across configured search fields.
    *   `ordering` (string, optional): Specify field(s) to order by (e.g., `?ordering=-published_at,title`).
*   **Response (Success):** `200 OK`
    ```json
    {
      "count": 15,
      "next": "/api/v1/content-instances/?page=2",
      "previous": null,
      "results": [
        {
          "id": "uuid-string",
          "content_type_api_id": "blog-post",
          "status": "published",
          "author_detail": { /* CMSUser object */ },
          "created_at": "iso-8601-timestamp",
          "updated_at": "iso-8601-timestamp",
          "published_at": "iso-8601-timestamp",
          "terms_detail": [ /* List of Term objects */ ],
          "content_data": {
            "title": { // Localizable field example
              "value": "My Blog Post Title",
              "language": "en" // Language code value was resolved from
            },
            "slug": "my-blog-post-title", // Non-localizable field example
            "body": {
                "value": "<p>Content body...</p>",
                "language": "en"
            }
            // ... other fields based on ContentType definition
          },
          "layout_components": null // Or list of components if it's a page type
        },
        // ... more content instances
      ]
    }
    ```
*   **Response (Error):** `400 Bad Request` (invalid filter/ordering), `404 Not Found` (if filtering by non-existent content type).

---

## Retrieve Single Content Instance

*   **Endpoint:** `GET /api/v1/content-instances/{instance_pk}/`
*   **Description:** Retrieves details for a specific content instance.
*   **Authentication:** Optional (Default: Read-only allowed).
*   **URL Parameters:**
    *   `instance_pk` (uuid, required): The unique ID of the `ContentInstance`.
*   **Query Parameters:**
    *   `lang` (string, optional): Specify the desired language code. See [Multilingual Support](#multilingual-support).
    *   `include_comments` (string, optional): Set to `approved` (e.g., `?include_comments=approved`) to embed approved comments in the response. *(Note: This parameter requires specific implementation in the ViewSet/Serializer)*.
*   **Response (Success):** `200 OK`
    ```json
    {
      "id": "uuid-string",
      "content_type_api_id": "landing-page",
      "status": "published",
      "author_detail": { /* CMSUser object */ },
      "created_at": "iso-8601-timestamp",
      "updated_at": "iso-8601-timestamp",
      "published_at": "iso-8601-timestamp",
      "terms_detail": [ /* List of Term objects */ ],
      "content_data": {
         // Standard fields for this content type...
         "headline": {
             "value": "Welcome!",
             "language": "en"
         }
      },
      "layout_components": [ // Example for a 'Page' type
        {
          "id": "page-component-uuid-1",
          "component_api_id": "hero_banner",
          "order": 0,
          "data": {
            "headline": "Main Hero Headline",
            "background_image_id": "media-asset-uuid",
            "button_text": "Learn More"
          }
        },
        {
          "id": "page-component-uuid-2",
          "component_api_id": "two_column_text",
          "order": 1,
          "data": {
            "left_column": "<p>Some text...</p>",
            "right_column": "<p>More text...</p>"
          }
        }
        // ... more components
      ],
      "comments": null // Or list of approved comments if ?include_comments=approved
    }
    ```
*   **Response (Error):** `404 Not Found`.

---

## List Content Types (Read-Only)

*   **Endpoint:** `GET /api/v1/content-types/`
*   **Description:** Retrieves a list of defined content types and their field definitions. Useful for understanding available content structures.
*   **Authentication:** Required (`IsAuthenticated`).
*   **Response (Success):** `200 OK`
    ```json
    [ // Paginated response structure omitted for brevity
      {
        "id": "uuid-string",
        "name": "Blog Post",
        "api_id": "blog-post",
        "description": "Standard blog article format.",
        "field_definitions": [
          {
            "id": "field-def-uuid-1",
            "name": "Title",
            "api_id": "title",
            "field_type": "text",
            "order": 0,
            "config": {"required": true, "localizable": true},
            "is_localizable": true,
            "is_required": true
          },
          // ... other field definitions
        ],
        "created_at": "iso-8601-timestamp",
        "updated_at": "iso-8601-timestamp"
      },
      // ... more content types
    ]
    ```

---

## Retrieve Single Content Type (Read-Only)

*   **Endpoint:** `GET /api/v1/content-types/{api_id}/`
*   **Description:** Retrieves details for a specific content type definition.
*   **Authentication:** Required (`IsAuthenticated`).
*   **URL Parameters:**
    *   `api_id` (string, required): The unique API ID of the `ContentType`.
*   **Response (Success):** `200 OK` (Returns a single object like the items in the list response above).
*   **Response (Error):** `404 Not Found`.

---