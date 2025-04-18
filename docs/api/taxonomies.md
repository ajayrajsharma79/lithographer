# API Documentation: Taxonomies & Terms

This section describes API endpoints for managing taxonomies (classification systems like categories or tags) and their associated terms. These endpoints are primarily intended for administrative or programmatic use.

**Authentication:** Requires authentication (CMS User Session or API Key). Permissions are typically restricted (e.g., Admins for Taxonomies, Editors/Admins for Terms).

---

## List Taxonomies

*   **Endpoint:** `GET /api/v1/taxonomies/`
*   **Description:** Retrieves a list of defined taxonomy systems.
*   **Authentication:** Required.
*   **Permissions:** Admin users (`IsAdminUser`).
*   **Query Parameters:**
    *   `page` (integer, optional): Page number for pagination.
    *   `search` (string, optional): Search by name or api_id.
*   **Response (Success):** `200 OK`
    ```json
    {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": "taxonomy-uuid-1",
          "name": "Categories",
          "api_id": "categories",
          "hierarchical": true,
          "content_types_api_ids": ["blog-post", "product"], // api_ids of associated ContentTypes
          "created_at": "iso-8601-timestamp",
          "updated_at": "iso-8601-timestamp"
        },
        {
          "id": "taxonomy-uuid-2",
          "name": "Tags",
          "api_id": "tags",
          "hierarchical": false,
          "content_types_api_ids": ["blog-post"],
          "created_at": "iso-8601-timestamp",
          "updated_at": "iso-8601-timestamp"
        }
      ]
    }
    ```
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`.

---

## Create Taxonomy

*   **Endpoint:** `POST /api/v1/taxonomies/`
*   **Description:** Creates a new taxonomy system.
*   **Authentication:** Required.
*   **Permissions:** Admin users (`IsAdminUser`).
*   **Request Body:** `application/json`
    ```json
    {
      "name": "Regions", // Required
      "api_id": "regions", // Optional, auto-generated if blank
      "hierarchical": true, // Optional, default false
      "content_types_api_ids": ["store-location"] // Optional list of ContentType api_ids
    }
    ```
*   **Response (Success):** `201 Created` (Returns the new Taxonomy object).
*   **Response (Error):** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`.

---

## Retrieve Taxonomy Details

*   **Endpoint:** `GET /api/v1/taxonomies/{api_id}/`
*   **Description:** Retrieves details for a specific taxonomy system.
*   **Authentication:** Required.
*   **Permissions:** Admin users (`IsAdminUser`).
*   **URL Parameters:**
    *   `api_id` (string, required): The unique API ID of the Taxonomy.
*   **Response (Success):** `200 OK` (Returns a single Taxonomy object).
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Update Taxonomy

*   **Endpoint:** `PUT /api/v1/taxonomies/{api_id}/`, `PATCH /api/v1/taxonomies/{api_id}/`
*   **Description:** Updates an existing taxonomy system.
*   **Authentication:** Required.
*   **Permissions:** Admin users (`IsAdminUser`).
*   **URL Parameters:**
    *   `api_id` (string, required): The unique API ID of the Taxonomy.
*   **Request Body:** `application/json` (Provide fields to update).
*   **Response (Success):** `200 OK` (Returns the updated Taxonomy object).
*   **Response (Error):** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Delete Taxonomy

*   **Endpoint:** `DELETE /api/v1/taxonomies/{api_id}/`
*   **Description:** Deletes a taxonomy system. Associated terms will also be deleted (cascade).
*   **Authentication:** Required.
*   **Permissions:** Admin users (`IsAdminUser`).
*   **URL Parameters:**
    *   `api_id` (string, required): The unique API ID of the Taxonomy.
*   **Response (Success):** `204 No Content`.
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---
---

## List Terms (within a Taxonomy)

*   **Endpoint:** `GET /api/v1/taxonomies/{taxonomy_api_id}/terms/`
*   **Description:** Retrieves a list of terms belonging to a specific taxonomy.
*   **Authentication:** Required.
*   **Permissions:** Editor/Admin users (`IsEditorUser`).
*   **URL Parameters:**
    *   `taxonomy_api_id` (string, required): The API ID of the parent Taxonomy.
*   **Query Parameters:**
    *   `page` (integer, optional): Page number for pagination.
    *   `search` (string, optional): Search term names/slugs.
*   **Response (Success):** `200 OK`
    ```json
    {
      "count": 5,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": "term-uuid-1",
          "taxonomy": "taxonomy-uuid-1", // Parent Taxonomy ID
          "taxonomy_api_id": "categories",
          "parent_id": null,
          "translated_names": {"en": "Technology", "fr": "Technologie"},
          "translated_slugs": {"en": "technology", "fr": "technologie"},
          "created_at": "iso-8601-timestamp",
          "updated_at": "iso-8601-timestamp"
        },
        // ... more terms
      ]
    }
    ```
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found` (if taxonomy_api_id is invalid).

---

## Create Term (within a Taxonomy)

*   **Endpoint:** `POST /api/v1/taxonomies/{taxonomy_api_id}/terms/`
*   **Description:** Creates a new term within the specified taxonomy.
*   **Authentication:** Required.
*   **Permissions:** Editor/Admin users (`IsEditorUser`).
*   **URL Parameters:**
    *   `taxonomy_api_id` (string, required): The API ID of the parent Taxonomy.
*   **Request Body:** `application/json`
    ```json
    {
      "parent_id": null, // Optional: UUID of parent term within the same taxonomy
      "translated_names": {"en": "New Term", "es": "Nuevo Término"}, // Required
      "translated_slugs": {"en": "new-term", "es": "nuevo-termino"} // Optional, auto-generated if blank
    }
    ```
*   **Response (Success):** `201 Created` (Returns the new Term object).
*   **Response (Error):** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Retrieve Term Details

*   **Endpoint:** `GET /api/v1/taxonomies/{taxonomy_api_id}/terms/{term_pk}/`
*   **Description:** Retrieves details for a specific term.
*   **Authentication:** Required.
*   **Permissions:** Editor/Admin users (`IsEditorUser`).
*   **URL Parameters:**
    *   `taxonomy_api_id` (string, required): API ID of the parent Taxonomy.
    *   `term_pk` (uuid, required): The unique ID of the Term.
*   **Response (Success):** `200 OK` (Returns a single Term object).
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Update Term

*   **Endpoint:** `PUT /api/v1/taxonomies/{taxonomy_api_id}/terms/{term_pk}/`, `PATCH /api/v1/taxonomies/{taxonomy_api_id}/terms/{term_pk}/`
*   **Description:** Updates an existing term.
*   **Authentication:** Required.
*   **Permissions:** Editor/Admin users (`IsEditorUser`).
*   **URL Parameters:**
    *   `taxonomy_api_id` (string, required): API ID of the parent Taxonomy.
    *   `term_pk` (uuid, required): The unique ID of the Term.
*   **Request Body:** `application/json` (Provide fields to update).
*   **Response (Success):** `200 OK` (Returns the updated Term object).
*   **Response (Error):** `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Delete Term

*   **Endpoint:** `DELETE /api/v1/taxonomies/{taxonomy_api_id}/terms/{term_pk}/`
*   **Description:** Deletes a term. Child terms (if any) may also be deleted depending on model definition (`on_delete`).
*   **Authentication:** Required.
*   **Permissions:** Editor/Admin users (`IsEditorUser`).
*   **URL Parameters:**
    *   `taxonomy_api_id` (string, required): API ID of the parent Taxonomy.
    *   `term_pk` (uuid, required): The unique ID of the Term.
*   **Response (Success):** `204 No Content`.
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---