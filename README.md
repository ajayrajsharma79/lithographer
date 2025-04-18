# Lithographer
Lithographer is a reusable, headless CMS framework powered by Python and Django. Features dynamic content modeling, multilingual support, visual layout building, and robust APIs.

## Getting Started

This guide covers the initial setup and basic usage of the Lithographer CMS Admin interface.

### 1. Initial Project Setup

Follow these steps to set up the project locally for development:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd lithographer
    ```

2.  **Create Virtual Environment:**
    It's highly recommended to use a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # On Linux/macOS
    # or .\.venv\Scripts\activate # On Windows
    ```

3.  **Install Dependencies:**
    Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    *   Copy the example environment file: `cp .env.example .env` (Assuming `.env.example` exists, otherwise create `.env` manually).
    *   Edit the `.env` file and update the following variables for your local setup:
        *   `SECRET_KEY`: Generate a new secret key.
        *   `DATABASE_URL`: Set the connection string for your PostgreSQL database (e.g., `postgres://user:password@localhost:5432/lithographer_db`). Ensure the database exists and the user has permissions.
        *   `REDIS_URL`: Set the connection string for your Redis instance (used for caching and Celery).
        *   Update other settings like `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` if needed.

5.  **Run Database Migrations:**
    Apply the initial database schema.
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser:**
    Create the initial administrator account for the CMS.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set the email, password, and other required fields for the admin user.

7.  **Run Development Server:**
    Start the Django development server.
    ```bash
    python manage.py runserver
    ```
    The server will typically be available at `http://127.0.0.1:8000/`.

### 2. Logging In

1.  Open your web browser and navigate to the admin interface, usually `http://127.0.0.1:8000/admin/`.
2.  Enter the email address and password you created for the superuser (or other CMS User accounts).
3.  Click "Log in".

### 3. System Configuration (Admin)

Global system settings and language management are configured within the Django Admin:

*   **Manage Languages:** Navigate to `Core` > `Languages`.
    *   **Add:** Click "Add Language". Provide the standard `Language Code` (e.g., `en`, `en-gb`, `fr`, `es-mx`) and a descriptive `Language Name`.
    *   **Activate/Deactivate:** Use the `Is active` checkbox. Only active languages will be available for content translation and selection.
    *   **Set Default:** Select one active language and use the "Set selected language as default" action (or ensure the `Is default` flag is set correctly, though direct editing might be disabled). The default language is used for fallback purposes.
*   **Configure System Settings:** Navigate to `Core` > `System Settings`. There should be only one entry. Click it to configure:
    *   `Site Name`: The public name of the website.
    *   `Default Language`: Select the primary language for the site from the *active* Languages defined above.
    *   `Timezone`: Set the default timezone for the application (e.g., 'UTC', 'America/New_York').
    *   `Default Content Status`: Choose the initial status assigned to new content entries (e.g., 'draft').
    *   `External Integrations Config`: A JSON field to store API keys or settings for third-party services (e.g., `{"google_analytics_id": "UA-XXXXX-Y"}`). Use with caution.

### 4. Managing API Keys (Admin)

API keys allow external systems (like an AI Agent or frontend application) to interact with the CMS API securely.

1.  Navigate to `Users` > `API Keys` in the admin interface.
2.  **Create Key:** Click "Add API Key".
    *   Select the `CMS User` this key should be associated with (determines permissions).
    *   Give the key a descriptive `Name` (e.g., "AI Blog Post Generator").
    *   Ensure `Is Active` is checked.
    *   Click "Save". The unique key string will be generated automatically (note: it's typically shown only once upon creation or only partially afterwards for security).
3.  **Manage Keys:** From the list view, you can:
    *   View existing keys (only a prefix is shown).
    *   Click on a key's name to edit its `Name` or `Is Active` status.
    *   Select keys and use the "Delete selected api keys" action to remove them.

### 5. Defining Content Structures (Admin)

This section covers how Administrators define the different types of content the CMS will manage.

1.  Navigate to `Content` > `Content Types`.
2.  **Create Content Type:** Click "Add Content Type".
    *   Enter a `Content Type Name` (e.g., "Blog Post", "Product Page", "Landing Page").
    *   The `API ID` will be auto-generated from the name (e.g., `blog-post`) but can be customized. This ID is used internally and in APIs.
    *   Add an optional `Description`.
3.  **Add Fields:** While creating or editing a Content Type, you'll see an inline section for `Field Definitions`:
    *   Click "Add another Field Definition".
    *   **Field Name:** Enter a user-friendly name (e.g., "Post Title", "Main Body", "Publication Date", "Featured Image", "Category").
    *   **API ID:** Auto-generated from the name (e.g., `post-title`), customizable. Used for API interaction.
    *   **Field Type:** Select the appropriate type from the dropdown (e.g., `Text`, `Rich Text`, `Date/DateTime`, `Media`, `Relationship`, `Select`).
    *   **Order:** Set a number to control the display order in the content editing form.
    *   **Configuration (JSON):** This field allows detailed settings. Enter valid JSON, for example:
        *   `{"required": true, "help_text": "The main title of the post.", "localizable": true}` (for Post Title)
        *   `{"localizable": true}` (for Main Body - Rich Text)
        *   `{"required": false}` (for Publication Date - Non-localizable)
        *   `{"allowed_media_types": ["image"]}` (for Featured Image - Media type)
        *   `{"allowed_content_types": ["author_profile"]}` (for Author - Relationship type, assuming an 'author_profile' Content Type exists)
        *   `{"select_options": ["Option 1", "Option 2"]}` (for a Select type field)
        *   **Crucially, set `"localizable": true` for any field whose content should be translated across different languages.** Fields without this flag (or set to `false`) will have only one value shared across all languages.
4.  **Save:** Save the Field Definition row and then save the Content Type. Repeat step 3 to add all necessary fields.
5.  **Reorder/Edit:** You can drag-and-drop the Field Definition rows to change their order or click on them to edit their configuration.

### 6. Managing Taxonomies (Admin/Editor)

Taxonomies allow you to categorize and organize content (e.g., categories, tags).

1.  Navigate to `Content` > `Taxonomies`.
2.  **Create Taxonomy:** Click "Add Taxonomy".
    *   Enter a `Taxonomy Name` (e.g., "Categories", "Tags").
    *   The `API ID` is auto-generated (e.g., `categories`).
    *   Check `Hierarchical` if terms within this taxonomy can have parent-child relationships (like categories). Leave unchecked for flat structures (like tags).
    *   **Associate with Content Types:** In the `Applicable Content Types` section, select the `ContentType`(s) that should be able to use this taxonomy (e.g., associate "Categories" with "Blog Post").
    *   Save the Taxonomy.
3.  Navigate to `Content` > `Terms`.
4.  **Add Term:** Click "Add Term".
    *   Select the `Taxonomy` this term belongs to (e.g., "Categories").
    *   **Translated Names (JSON):** Enter the term name for each *active* language defined in the system, using the language code as the key. Example: `{"en": "Technology", "fr": "Technologie"}`. (*Note: Requires Admin UI customization for a user-friendly translation experience.*)
    *   **Translated Slugs (JSON):** Enter URL-friendly slugs for each language. Example: `{"en": "technology", "fr": "technologie"}`. Slugs are auto-generated from names if left blank. (*Note: Requires Admin UI customization.*)
    *   **Parent Term:** If the taxonomy is hierarchical, you can select an existing term from the *same taxonomy* to be the parent.
    *   Save the Term. Repeat to add all necessary terms.
5.  **Manage Hierarchy:** Edit existing terms to change their parent.
6.  **Translate Terms:** Edit existing terms to add or modify names/slugs in the JSON fields for different languages.

### 7. Managing Content Entries (Editor/Admin)

Once Content Types and Taxonomies are defined, Editors and Administrators can create and manage content.

1.  Navigate to `Content` > `Content Instances`.
2.  **Create Content:** Click "Add Content Instance".
    *   Select the `Content Type` you want to create (e.g., "Blog Post").
    *   The form will dynamically display the fields defined for that Content Type. (*Note: Requires significant Admin UI customization for a user-friendly experience, especially for multilingual fields and layout building.*)
3.  **Editing Content (Multilingual):**
    *   The editing form needs customization to properly handle multilingual content. Ideally, it would display:
        *   **Non-Localizable Fields:** Shown once, as their value applies to all languages.
        *   **Localizable Fields:** Presented grouped by language (e.g., using tabs labeled 'en', 'fr', etc., based on active languages) or in side-by-side sections. Each language section would contain the input widgets for all fields marked as `localizable`.
    *   Fill in the data for each field. For localizable fields, switch between language tabs/sections to provide the translated content.
    *   **Taxonomy Terms:** If taxonomies are associated with the Content Type, you'll see a section (likely a multi-select box) to choose relevant `Term`s (e.g., check "Technology" under "Categories").
    *   **Media/Relationships:** For fields linked to Media or other Content Instances, use the provided widgets (e.g., a lookup popup or dropdown) to select the related items. (*Note: Media selection widget requires further implementation.*)
4.  **Managing Status:** Select the desired `Status` from the dropdown (e.g., "Draft", "Published"). Permissions might restrict which statuses are available. The default status is set in System Settings.
5.  **Saving:** Click "Save", "Save and continue editing", or "Save and add another".
6.  **Viewing Version History:**
    *   When viewing an existing Content Instance in the admin, look for a "History" button or link (standard Django admin feature).
    *   This will show a list of saved versions, including the timestamp, user who made the change, and any associated version message.
    *   *Note: Reverting to a previous version might require custom actions not yet implemented in the basic admin.*

### 8. Content Ingestion API (For Developers/External Systems)

Lithographer provides an API endpoint for programmatically creating content. External systems (like AI agents or other applications) can send data conforming to a defined `ContentType` to create new `ContentInstance`s.

*   **Purpose:** Automate content creation.
*   **Authentication:** Requires a valid API Key associated with a CMS User.
*   **Endpoint (Conceptual):** `POST /api/v1/content-instances/`
*   **Payload:** The request body should include the `content_type` (ID or API ID) and a `content_data` object containing the field data, structured according to the Content Type's field definitions and localization requirements. Example:
    ```json
    {
      "content_type": "<content_type_uuid_or_api_id>",
      "status": "draft", // Optional initial status
      "content_data": {
        "post-title": { // Localizable field
          "en": "My English Title",
          "fr": "Mon Titre Français"
        },
        "slug": "my-english-title", // Non-localizable field
        "main-body": {
           "en": "<p>English content...</p>",
           "fr": "<p>Contenu français...</p>"
        }
      },
      "term_ids": ["<term_uuid_1>", "<term_uuid_2>"] // Optional Term IDs
    }
    ```

Refer to the API documentation (if available) or explore the `/api/v1/` endpoint for detailed request/response formats.

### 9. Managing Media Assets (Admin/Editor)

The Media Library allows uploading and organizing files (images, documents, etc.) used within the content.

1.  Navigate to `Media` > `Media Assets`.
2.  **Uploading Assets:**
    *   Click "Add Media Asset".
    *   **Translated Metadata:** Enter `Translated Title`, `Translated Alt Text` (important for images), and `Translated Caption` using JSON format, providing key-value pairs for each active language (e.g., `{"en": "My Image Title", "fr": "Mon Titre d'Image"}`). (*Note: Requires Admin UI customization for a user-friendly translation experience.*)
    *   Click "Choose File" to select a file from your computer.
    *   Optionally, select a `Folder` for organization and relevant `Media Tags`.
    *   Click "Save". The file will be uploaded, and metadata (filename, size, dimensions for images) will be extracted (potentially asynchronously via a background task).
3.  **Browsing & Searching:**
    *   The `Media Assets` list view displays thumbnails (for images), titles/filenames, and other details.
    *   Use the filters on the right to filter by `MIME type`, `Folder`, `Upload timestamp`, or `Tags`.
    *   Use the search bar at the top to search by title, filename, alt text, caption, tags, or uploader email.
    *   *(Folder navigation within the list view might require UI customization)*. Navigate to `Media` > `Folders` to manage the folder structure itself.
4.  **Editing Metadata:**
    *   Click on the title/filename of an asset in the list view.
    *   You can edit the translated `Title`, `Alt Text`, `Caption` (as JSON), assign it to a `Folder`, and manage associated `Media Tags`.
    *   The `Custom Metadata` field allows adding arbitrary key-value pairs as JSON.
    *   Save your changes.
5.  **Managing Tags:**
    *   Navigate to `Media` > `Media Tags`.
    *   Click "Add Media Tag" to create new tags (e.g., "Logo", "Screenshot", "Icon").
    *   Edit or delete existing tags from the list view.
6.  **Selecting Media in Content:**
    *   When editing a `Content Instance` that has a field of type `Media`, you will typically use a specific widget (e.g., a button labeled "Choose Media" or similar). (*Note: This widget requires implementation.*)
    *   Clicking this widget should open a media browser/selector popup allowing you to browse or search the Media Library and select the desired asset.

### 10. User & Role Management (Admin)

Administrators manage CMS users, roles, permissions, and front-end users.

1.  **Managing CMS Users:**
    *   Navigate to `Users` > `CMS Users`.
    *   **Add User:** Click "Add CMS User". Enter email, first/last name, set a password, and assign `Roles`. You can also control `is_staff` and `is_superuser` status here.
    *   **Edit User:** Click on a user's email to edit their details, change their password, activate/deactivate them (`Is active` flag), or modify their assigned `Roles`.
2.  **Managing Roles & Permissions:**
    *   Navigate to `Users` > `Roles`.
    *   **Add Role:** Click "Add Role". Enter a `Name` (e.g., "Content Publisher", "Reviewer") and `Description`.
    *   **Assign Permissions:** In the `Permissions` field (a JSON text area), enter a list of permission strings that users with this role should have. Examples:
        *   `["content.add_contentinstance", "content.change_contentinstance"]` (Basic editing)
        *   `["content.publish_blogpost"]` (Custom permission for publishing specific types - requires code implementation for checking)
        *   `["media.add_mediaasset", "media.change_mediaasset"]`
        *   Use `["*"]` to grant all permissions (use with caution).
        *   *(Note: A more user-friendly interface for selecting permissions is recommended for future development.)*
    *   **Edit Role:** Click on a role name to modify its description or permissions. System roles (like Administrator) cannot be deleted.
3.  **Managing Front-End Users:**
    *   Navigate to `Frontend Users` > `Front-End Users`.
    *   View the list of registered front-end users.
    *   Click on a username to view/edit their profile details (First Name, Last Name, Display Name).
    *   Change the user's `Status` (Active, Inactive, Banned).
    *   Activate/Deactivate users using the `Is active` flag.
    *   *(Note: Adding front-end users via the admin is disabled by default; use the registration API.)*

### 11. Defining Reusable Components (Admin)

Administrators can define reusable front-end components that Editors can use to build page layouts.

1.  Navigate to `Components` > `Component Definitions`.
2.  **Create Component Definition:** Click "Add Component Definition".
    *   Enter a `Component Name` (e.g., "Hero Banner", "Call To Action", "Two Column Text").
    *   The `API ID` is auto-generated (e.g., `hero-banner`) but can be customized. This ID is used by front-end developers.
    *   Add an optional `Description` and `Icon Class/URL` (for potential use in the admin UI).
3.  **Add Component Fields:** While creating or editing a Component Definition, use the inline `Component Field Definitions` section:
    *   Click "Add another Component Field Definition".
    *   Define the configurable fields for this component (e.g., for a 'Hero Banner': 'Headline' (Text), 'Sub-headline' (Text), 'Background Image' (Media), 'Button Text' (Text), 'Button Link' (URL)).
    *   For each field, set the `Field Name`, `API ID`, `Field Type`, `Order`, and any specific `Configuration` (JSON) like `required`, `help_text`, `default_value`.
4.  **Save:** Save the field definitions and the component definition.

### 12. Building Page Layouts (Editor)

For Content Types designated as "pages" (e.g., "Landing Page"), Editors can assemble layouts using the defined Components.

1.  Navigate to `Content` > `Content Instances` and add or edit an instance of a page-like Content Type.
2.  **Layout Editor:** Look for the "Page Components" section (or similar) within the admin form. (*Note: This section requires significant Admin UI customization for a user-friendly drag-and-drop, component configuration experience.*)
3.  **Add Component:** Use the "Add another Page Component" button (or a potentially more visual "Add Component" interface).
    *   Select the desired `Component Definition` (e.g., "Hero Banner") from the dropdown.
    *   **Configure Data:** A form should appear (dynamically generated based on the component's fields) allowing you to enter the content for this specific instance of the component (e.g., type the headline, select the background image). This data is saved in the `Data` JSON field.
4.  **Reorder Components:** Use drag-and-drop (if implemented via custom JS) or manually edit the `Order` number for each component to control its position on the page.
5.  **Remove Components:** Use the delete checkbox/button associated with each component instance in the inline editor.
6.  **Save:** Save the Content Instance to persist the layout changes.

### 13. Comment Moderation (Admin/Moderator)

Comments submitted via the API require moderation before appearing on the front-end.

1.  Navigate to `Comments` > `Comments`.
2.  The list view defaults to showing the newest comments first. Use the `Status` filter on the right to view only `Pending` comments (the moderation queue).
3.  For each comment, you can see the user, an excerpt of the comment, and a link to the content it was posted on.
4.  **Moderate:**
    *   **Quick Change:** Select the desired status (`Approved`, `Rejected`, `Spam`) from the dropdown in the `Status` column and click "Save" at the bottom of the list.
    *   **Bulk Actions:** Select multiple comments using the checkboxes, then choose an action ("Approve selected comments", "Reject selected comments", "Mark selected comments as spam") from the "Actions" dropdown at the top and click "Go".
    *   **Edit/Detail View:** Click on the user link or comment excerpt to view the full comment details. From here, you can edit the comment `Body` or change the `Status` before saving.

### 14. Webhook Configuration (Admin)

Webhooks allow external services to be notified when specific events occur within the CMS.

1.  Navigate to `Webhooks` > `Webhook Endpoints`.
2.  **Create Endpoint:** Click "Add Webhook Endpoint".
    *   `Target URL`: Enter the full URL of the external service that should receive notifications.
    *   `Subscribed Events (JSON)`: Enter a JSON list of event names this endpoint should listen for (e.g., `["content_published", "media_uploaded"]`). Use `["*"]` to subscribe to all events. Available events include: `content_published`, `content_updated`, `content_deleted`, `media_uploaded`, `media_deleted`, `comment_submitted`, `comment_approved`. (*Note: Requires Admin UI customization for a user-friendly event selection experience.*)
    *   `Is Active`: Ensure this is checked for the webhook to receive events.
    *   `Secret`: Enter a strong secret string. This will be used to generate a signature sent with each webhook request, allowing the receiving service to verify the request originated from Lithographer.
    *   Save the endpoint.
3.  **Manage Endpoints:** View, edit (URL, events, active status, secret), or delete existing endpoints from the list view.
4.  **View Delivery Logs:** Navigate to `Webhooks` > `Webhook Event Logs`.
    *   This page lists all recent webhook delivery attempts.
    *   View the `Timestamp`, `Endpoint URL`, `Event Type`, delivery `Status` (Success/Failed), and the HTTP `Response Status Code` received from the target URL.
    *   Use the filters to narrow down logs by status, event type, date, or endpoint.
    *   Click on an entry to view more details, including the request headers/payload and response headers/body (may be truncated). This is useful for debugging delivery issues.

### 15. Developer Notes

*   **Multilingual API Usage:** When querying content via the Content Delivery API (e.g., `/api/v1/content-instances/`), use the `lang` query parameter (e.g., `?lang=fr`, `?lang=en-GB`) to request content for a specific language. The API implements fallback logic (requested locale -> base language -> site default -> site default base -> first available). Localized fields in the response indicate the language code used (e.g., `{"value": "Bonjour", "language": "fr"}`).
*   **Layout Data in API:** When fetching a `ContentInstance` that uses the layout builder (e.g., a "Page"), the response will include a `layout_components` field. This field contains an ordered list of component instances on the page. Each item includes the `component_api_id`, the configured `data` (JSON object), and the `order`. Front-end applications use this data to render the page dynamically.
*   **Comment API:** Authenticated front-end users can submit comments via `POST /api/v1/content-instances/<instance_pk>/comments/` with a payload like `{"body": "This is my comment", "parent_id": "<optional_parent_comment_uuid>"}`.
*   **Webhook Event Triggering:** Events are typically triggered asynchronously using Celery tasks initiated by Django signals (`post_save`, `post_delete`) attached to relevant models (`ContentInstance`, `MediaAsset`, `Comment`). See `apps/comments/signals.py` and `apps/webhooks/signals.py` (or signals within originating apps).
*   **Webhook Payload & Signature:** Webhooks are sent as `POST` requests with a JSON body containing `event` (string), `timestamp` (ISO 8601 string), and `data` (object with event-specific details). If a secret is configured for the endpoint, the request will include an `X-Lithographer-Signature-256` header containing an HMAC-SHA256 signature of the raw JSON payload body, calculated using the secret. Recipients should validate this signature.
