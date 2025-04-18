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

### 3. Basic System Configuration (Admin)

Initial system settings are managed within the Django Admin:

*   **Languages:** Navigate to `Core` > `Languages`. Here you can define the languages available for content localization (e.g., add 'English' with code 'en', 'French' with code 'fr'). Mark one language as default and ensure languages are active to be used.
*   **System Settings:** Navigate to `Core` > `System Settings`. There should be only one entry. Here you can configure the site name, default site language (selecting from active Languages), and the default timezone.

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
    *   Enter a `Content Type Name` (e.g., "Blog Post", "Product Page").
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
        *   `{"required": false}` (for Publication Date)
        *   `{"allowed_media_types": ["image"]}` (for Featured Image - Media type)
        *   `{"allowed_content_types": ["author_profile"]}` (for Author - Relationship type, assuming an 'author_profile' Content Type exists)
        *   `{"select_options": ["Option 1", "Option 2"]}` (for a Select type field)
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
    *   **Translated Names (JSON):** Enter the term name for each defined language, e.g., `{"en": "Technology", "fr": "Technologie"}`.
    *   **Translated Slugs (JSON):** Enter URL-friendly slugs for each language, e.g., `{"en": "technology", "fr": "technologie"}`. Slugs are auto-generated from names if left blank.
    *   **Parent Term:** If the taxonomy is hierarchical, you can select an existing term from the *same taxonomy* to be the parent.
    *   Save the Term. Repeat to add all necessary terms.
5.  **Manage Hierarchy:** Edit existing terms to change their parent.
6.  **Translate Terms:** Edit existing terms to add or modify names/slugs in the JSON fields for different languages.

### 7. Managing Content Entries (Editor/Admin)

Once Content Types and Taxonomies are defined, Editors and Administrators can create and manage content.

1.  Navigate to `Content` > `Content Instances`.
2.  **Create Content:** Click "Add Content Instance".
    *   Select the `Content Type` you want to create (e.g., "Blog Post").
    *   The form will dynamically display the fields defined for that Content Type.
3.  **Editing Content:**
    *   Fill in the data for each field using the appropriate input widget (text box, rich text editor, date picker, etc.).
    *   **Multilingual Fields:** For fields marked as `localizable` in their definition, you will likely see tabs or separate input areas for each active language defined in the system. Enter the content specific to each language. Non-localizable fields will have only one input area.
    *   **Taxonomy Terms:** If taxonomies are associated with the Content Type, you'll see a section (likely a multi-select box) to choose relevant `Term`s (e.g., check "Technology" under "Categories").
    *   **Media/Relationships:** For fields linked to Media or other Content Instances, use the provided widgets (e.g., a lookup popup or dropdown) to select the related items. (Media Library functionality details TBD).
4.  **Managing Status:** Select the desired `Status` from the dropdown (e.g., "Draft", "Published"). Permissions might restrict which statuses are available.
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
