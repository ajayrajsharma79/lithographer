# API Documentation: Media Library

This section covers API endpoints for managing media assets (images, documents, etc.) within the Lithographer CMS.

**Authentication:** Most endpoints require authentication (CMS User Session or API Key). Permissions may vary based on the action (e.g., only Admins or the original uploader can delete).

---

## List Media Assets

*   **Endpoint:** `GET /api/v1/media/assets/`
*   **Description:** Retrieves a paginated list of media assets.
*   **Authentication:** Required (CMS User Session/API Key).
*   **Permissions:** Authenticated users can list assets.
*   **Query Parameters:**
    *   `page` (integer, optional): Page number for pagination.
    *   `folder` (uuid, optional): Filter by Folder ID.
    *   `mime_type` (string, optional): Filter by MIME type (e.g., `image/jpeg`, `application/pdf`).
    *   `tags` (uuid, optional): Filter by MediaTag ID.
    *   `uploader` (uuid, optional): Filter by the uploading CMSUser ID.
    *   `search` (string, optional): Search across title, filename, alt text, caption, tags.
    *   `ordering` (string, optional): Order by fields like `upload_timestamp`, `title`, `filename`, `size`. (e.g., `?ordering=-upload_timestamp`).
*   **Response (Success):** `200 OK`
    ```json
    {
      "count": 5,
      "next": null,
      "previous": null,
      "results": [
        {
          "id": "asset-uuid-1",
          "translated_title": {"en": "My Image"},
          "translated_alt_text": {"en": "Alt text for my image"},
          "translated_caption": {},
          "file_url": "/media/media_assets/...",
          "filename": "my_image.jpg",
          "mime_type": "image/jpeg",
          "size": 102400, // bytes
          "width": 800,
          "height": 600,
          "dimensions": {"width": 800, "height": 600},
          "folder_id": "folder-uuid-1",
          "tag_ids": ["tag-uuid-1"],
          "custom_metadata": {"source": "camera"},
          "uploader_detail": { /* CMSUser object */ },
          "upload_timestamp": "iso-8601-timestamp",
          "optimized_versions": {"thumbnail": "/media/..."}
        },
        // ... more assets
      ]
    }
    ```
*   **Response (Error):** `400 Bad Request` (invalid filter/ordering), `401 Unauthorized`, `403 Forbidden`.

---

## Upload Media Asset

*   **Endpoint:** `POST /api/v1/media/assets/`
*   **Description:** Uploads a new file to the media library. Metadata extraction and optimization occur asynchronously.
*   **Authentication:** Required (CMS User Session/API Key).
*   **Permissions:** Requires permission to add media assets (e.g., `media.add_mediaasset`).
*   **Request Body:** `multipart/form-data`
    *   `file` (file, required): The actual file being uploaded.
    *   `translated_title` (string, optional): JSON string for titles (e.g., `{"en": "Title"}`).
    *   `translated_alt_text` (string, optional): JSON string for alt texts.
    *   `translated_caption` (string, optional): JSON string for captions.
    *   `folder_id` (uuid, optional): ID of the folder to place the asset in.
    *   `tag_ids` (list[uuid], optional): List of MediaTag IDs to associate.
    *   `custom_metadata` (string, optional): JSON string for custom data.
*   **Response (Success):** `201 Created`
    *   Returns the representation of the newly created `MediaAsset` (similar to the list response item), potentially with some metadata fields (like `size`, `width`, `height`, `mime_type`, `optimized_versions`) being null initially until the background task completes.
*   **Response (Error):** `400 Bad Request` (missing file, invalid JSON, invalid IDs), `401 Unauthorized`, `403 Forbidden`.

---

## Retrieve Media Asset Details

*   **Endpoint:** `GET /api/v1/media/assets/{asset_pk}/`
*   **Description:** Retrieves details for a specific media asset.
*   **Authentication:** Required (CMS User Session/API Key).
*   **Permissions:** Authenticated users can retrieve assets.
*   **URL Parameters:**
    *   `asset_pk` (uuid, required): The unique ID of the `MediaAsset`.
*   **Response (Success):** `200 OK`
    *   Returns a single `MediaAsset` object (structure same as list response item).
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Update Media Asset Metadata

*   **Endpoint:** `PUT /api/v1/media/assets/{asset_pk}/`, `PATCH /api/v1/media/assets/{asset_pk}/`
*   **Description:** Updates the metadata (title, alt, caption, folder, tags, custom metadata) of a specific media asset. The file itself cannot be changed via this endpoint.
*   **Authentication:** Required (CMS User Session/API Key).
*   **Permissions:** Requires permission to change the asset (e.g., `media.change_mediaasset`) OR must be the original uploader.
*   **URL Parameters:**
    *   `asset_pk` (uuid, required): The unique ID of the `MediaAsset`.
*   **Request Body:** `application/json`
    *   Include fields to be updated. `PUT` requires all writable fields, `PATCH` allows partial updates.
    ```json
    // Example PATCH request
    {
      "translated_title": {"en": "Updated Title", "fr": "Titre Mis à Jour"},
      "tag_ids": ["tag-uuid-1", "tag-uuid-new"],
      "folder_id": "new-folder-uuid"
    }
    ```
*   **Response (Success):** `200 OK`
    *   Returns the full, updated representation of the `MediaAsset`.
*   **Response (Error):** `400 Bad Request` (invalid data), `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Delete Media Asset

*   **Endpoint:** `DELETE /api/v1/media/assets/{asset_pk}/`
*   **Description:** Deletes a specific media asset, including its file from storage.
*   **Authentication:** Required (CMS User Session/API Key).
*   **Permissions:** Requires permission to delete the asset (e.g., `media.delete_mediaasset`) OR must be the original uploader.
*   **URL Parameters:**
    *   `asset_pk` (uuid, required): The unique ID of the `MediaAsset`.
*   **Response (Success):** `204 No Content`
*   **Response (Error):** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

---

## Manage Folders & Tags

Endpoints for managing Folders (`/api/v1/media/folders/`) and Media Tags (`/api/v1/media/tags/`) follow standard DRF ModelViewSet patterns (LIST, CREATE, RETRIEVE, UPDATE, DELETE). Access is typically restricted to Administrators. Refer to the browsable API or standard DRF documentation for details.

---