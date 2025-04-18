# API Documentation: Comments

This section describes the API endpoint for submitting comments on content instances.

**Authentication:** Requires JWT Bearer token authentication for a logged-in `FrontEndUser`.

---

## Submit Comment

*   **Endpoint:** `POST /api/v1/content-instances/{instance_pk}/comments/`
*   **Description:** Allows an authenticated front-end user to submit a new comment or a reply to an existing comment on a specific content instance. Submitted comments typically start with a 'Pending' status and require moderation.
*   **Authentication:** JWT Bearer Token required (`Authorization: Bearer <access_token>`).
*   **Permissions:** Requires user to be an authenticated `FrontEndUser`.
*   **URL Parameters:**
    *   `instance_pk` (uuid, required): The unique ID of the `ContentInstance` being commented on.
*   **Request Body:** `application/json`
    ```json
    {
      "body": "This is my insightful comment!",
      "parent_id": null // Or the UUID of the comment being replied to
    }
    ```
    *   `body` (string, required): The text content of the comment.
    *   `parent_id` (uuid, optional): The ID of the parent comment if this is a reply. Omit or set to `null` for a top-level comment.
*   **Response (Success):** `201 Created`
    *   Returns the representation of the newly created comment, including its ID and initial 'Pending' status.
    ```json
    {
      "id": "new-comment-uuid",
      "content_instance": "content-instance-uuid",
      "user": "frontend-user-uuid", // User who submitted
      "user_detail": { /* FrontEndUser object */ },
      "parent": null, // Or parent comment UUID if it was a reply
      "parent_id": null, // Write-only field, not usually in response
      "body": "This is my insightful comment!",
      "status": "pending",
      "submission_timestamp": "iso-8601-timestamp"
    }
    ```
*   **Response (Error):**
    *   `400 Bad Request`: Missing `body`, invalid `parent_id` (e.g., doesn't belong to the same `instance_pk`).
    *   `401 Unauthorized`: Invalid or missing JWT token.
    *   `403 Forbidden`: Authenticated user is not a `FrontEndUser`.
    *   `404 Not Found`: The specified `instance_pk` or `parent_id` does not exist.

---

## Listing Comments

Approved comments are typically retrieved as part of the Content Delivery API response for a specific content instance, by using the `?include_comments=approved` query parameter on the content instance detail endpoint (e.g., `GET /api/v1/content-instances/{instance_pk}/?include_comments=approved`). See [Content Delivery](./content_delivery.md) documentation.

---