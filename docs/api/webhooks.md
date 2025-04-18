# API Documentation: Webhooks (Receiving)

Lithographer can send notifications to external services via webhooks when certain events occur within the CMS. This document describes the format of the webhook requests sent *by* Lithographer and how receiving services should handle them.

**Note:** Lithographer also provides API endpoints for *managing* webhook configurations (see [Admin/CMS Management](./admin.md)), but this document focuses on what a *recipient* of a webhook needs to know.

---

## Receiving Webhook Requests

When an event occurs in Lithographer that an endpoint is subscribed to, Lithographer will send an HTTP `POST` request to the configured `Target URL`.

*   **Method:** `POST`
*   **Content-Type:** `application/json`
*   **User-Agent:** `Lithographer-Webhook-Agent/1.0 (+<site_id>)` (Example)

---

## Request Body (Payload)

The request body will be a JSON object with the following structure:

```json
{
  "event": "event_name_string",
  "timestamp": "iso-8601-timestamp",
  "data": {
    // Event-specific data payload
    // Structure varies depending on the 'event' type
  }
}
```

*   `event` (string): The name of the event that triggered the webhook (e.g., `content_published`, `media_uploaded`, `comment_approved`). See list below.
*   `timestamp` (string): ISO 8601 formatted timestamp indicating when the event occurred or was triggered.
*   `data` (object): An object containing data relevant to the specific event.

### Example Event Payloads:

*   **`content_published` / `content_updated`:**
    ```json
    {
      "event": "content_published",
      "timestamp": "...",
      "data": {
        "content_instance_id": "uuid-string",
        "content_type_api_id": "blog-post",
        "status": "published",
        "updated_at": "iso-8601-timestamp"
        // Additional relevant fields might be included
      }
    }
    ```
*   **`content_deleted`:**
    ```json
    {
      "event": "content_deleted",
      "timestamp": "...",
      "data": {
        "content_instance_id": "uuid-string",
        "content_type_api_id": "blog-post"
      }
    }
    ```
*   **`media_uploaded`:**
    ```json
    {
      "event": "media_uploaded",
      "timestamp": "...",
      "data": {
        "media_asset_id": "uuid-string",
        "filename": "my_image.jpg",
        "mime_type": "image/jpeg",
        "size": 102400,
        "uploader_id": "cms-user-uuid"
      }
    }
    ```
*   **`media_deleted`:**
    ```json
    {
      "event": "media_deleted",
      "timestamp": "...",
      "data": {
        "media_asset_id": "uuid-string",
        "filename": "my_image.jpg"
      }
    }
    ```
*   **`comment_submitted` / `comment_approved`:**
    ```json
    {
      "event": "comment_approved",
      "timestamp": "...",
      "data": {
        "comment_id": "uuid-string",
        "content_instance_id": "uuid-string",
        "user_id": "frontend-user-uuid",
        "status": "approved",
        "body_excerpt": "This is my insightful comment!...",
        "submission_timestamp": "iso-8601-timestamp"
      }
    }
    ```

*(Note: Payload structures are illustrative and may evolve.)*

---

## Signature Verification (Security)

To ensure webhook requests genuinely originate from your Lithographer instance and haven't been tampered with, Lithographer includes a signature in the request headers if a `Secret` was configured for the `WebhookEndpoint`.

*   **Header Name:** `X-Lithographer-Signature-256`
*   **Format:** `sha256=<hmac_sha256_signature>`
*   **Calculation:** The signature is an HMAC (Hash-based Message Authentication Code) generated using the SHA-256 hash function.
    1.  The **key** is the `Secret` configured for the Webhook Endpoint in the Lithographer Admin UI.
    2.  The **message** is the raw JSON payload body sent in the `POST` request.

**Verification Steps (Receiving Service):**

1.  Extract the timestamp and signature(s) from the header(s). Consider checking the timestamp to prevent replay attacks (allow a small tolerance).
2.  Prepare the `signed_payload` string. This is the raw JSON body received in the request. **It's crucial to use the raw body, not a re-encoded version.**
3.  Compute an HMAC digest using SHA-256. Use the endpoint's configured `Secret` (which you must store securely on your receiving service) as the key and the `signed_payload` string as the message.
4.  Compare the computed digest (in hexadecimal format) with the signature provided in the `X-Lithographer-Signature-256` header (after the `sha256=` prefix). Use a secure comparison function to prevent timing attacks.
5.  If the signatures match, the webhook is verified. If they don't match, discard the request as it may be malicious or corrupted.

---

## Responding to Webhooks

Your endpoint should respond promptly to webhook requests to acknowledge receipt.

*   **Success:** Return a `2xx` HTTP status code (e.g., `200 OK`, `202 Accepted`, `204 No Content`) within a reasonable timeframe (e.g., less than the `WEBHOOK_TIMEOUT` configured in Lithographer, typically 5-10 seconds). Lithographer logs this as a successful delivery.
*   **Failure:** If your service encounters an error processing the webhook, return an appropriate `4xx` or `5xx` status code. Lithographer will log the delivery as failed and may retry based on its configuration (especially for `5xx` errors).

**Best Practice:** Acknowledge receipt immediately with a `2xx` response and then process the webhook payload asynchronously (e.g., using a background job queue) to avoid timeouts and handle potential processing delays gracefully.

---

## Available Event Types (Current List)

*   `content_published`
*   `content_updated`
*   `content_deleted`
*   `media_uploaded`
*   `media_deleted`
*   `comment_submitted`
*   `comment_approved`

*(This list may expand as new features are added.)*

---