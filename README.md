# Lithographer (Experimental CMS - Not for production)
Lithographer is a reusable, headless CMS framework, it is powered by Python and Django, it features dynamic content modeling, multilingual support, visual layout building, and robust APIs. It is completely coded by AI with no human interfarence. 

This is part of my on-going experiments with various AI Models for testing thier capabities and my skills to develop AI Agents.  

## Features

Lithographer is a reusable, general-purpose Content Management System (CMS) framework designed to be a robust, scalable, and extensible platform for various content-driven websites and applications. Built with a headless-first approach, it provides powerful tools for administrators, editors, and developers while offering flexibility for diverse content needs.

**Core Capabilities:**

* **Dynamic Content Modeling:**
    * Administrators can define custom **Content Types** (e.g., Blog Post, Recipe, Product) with unique fields directly through the Admin UI.
    * Supports a comprehensive set of **Field Types**: Text, Rich Text, Number, Date, Boolean, Email, URL, Media, Relationships, Select Lists, Repeatable Structured Data (JSON), etc.
    * Configure fields with validation rules, default values, help text, required/unique flags, and **localization settings**.

* **Content Management:**
    * Intuitive Admin UI for **CRUD operations** (Create, Read, Update, Delete) on content instances.
    * **API endpoint** for secure, programmatic content ingestion from external systems (like AI agents).
    * Configurable **Content Workflows** with custom statuses (e.g., Draft, Review, Published) and role-based transitions.
    * **Content Versioning** to track changes, compare versions, and revert to previous states, accounting for language variations.

* **Multilingual Support:**
    * Define multiple **languages/locales** for the CMS instance.
    * Mark specific fields in Content Types as **"localizable"** to enable translation.
    * Admin interface designed for easy side-by-side or tabbed **content translation**.
    * **Taxonomy terms** can also be localized.
    * APIs support **language-specific content fetching** with configurable fallback logic.

* **Taxonomy Management:**
    * Create custom **taxonomy systems** (e.g., Categories, Tags) via the UI.
    * Supports both **hierarchical** (e.g., nested categories) and flat structures.
    * Associate taxonomies with specific Content Types.

* **Advanced Media Library (DAM):**
    * Central library for uploading and managing images, videos, and documents.
    * Features include **folder organization**, bulk uploads, **advanced search/filtering**, metadata editing (alt text, captions, custom fields), and **media tagging**.
    * Configurable **image optimization** profiles (resizing, WebP conversion).
    * (Optional) Media asset versioning.

* **User Management & Access Control:**
    * Manage **CMS Users** with predefined roles (Admin, Editor, Moderator) and support for **custom roles**.
    * **Granular Permission System** controlling access to system settings, content types, specific content instances (per type/language), media, comments, layouts, etc.
    * Separate management and **API for Front-End Users**, including registration, login (JWT/Session), password reset, and profile management.
    * Secure **API Key Management** for external systems.

* **Headless API Delivery:**
    * Secure, performant **Content Delivery API** (RESTful and/or GraphQL) to serve content instances.
    * Supports advanced **filtering, sorting, pagination, language filtering,** and field selection.
    * Mechanisms for **previewing** content and layouts before publishing.
    * Manages **localizable SEO fields** (meta titles, descriptions, slugs) and provides data for sitemaps.

* **Visual Layout Builder:**
    * Define reusable front-end **Components/Blocks** (e.g., Hero Banner, Image Gallery, CTA) with configurable fields.
    * Assemble page layouts using an intuitive **Layout Editor** within specific Page content types, allowing editors to add, configure, reorder, and remove components.
    * The **structured layout data** is delivered via the API for front-end rendering.

* **Community Features:**
    * Store and manage **comments** associated with content instances.
    * **API endpoint** for front-end applications to submit comments (requires front-end user authentication).
    * **Moderation queue** and actions (Approve, Reject, Spam, Edit, Delete) in the Admin UI.
    * Optionally include **approved comments** in the Content Delivery API response.

* **Webhooks:**
    * Trigger notifications to external URLs based on configurable **system events** (e.g., Content Published, Media Uploaded, Comment Approved).
    * Admin UI for configuring webhook endpoints, associated events, and viewing delivery logs.
    * Secure payload delivery (e.g., using signatures).

Built on a modern stack (Django, PostgreSQL, DRF/GraphQL, Celery, Redis), Lithographer aims for high performance, scalability, security, and maintainability.

## Documentation

*   **[Getting Started Guide](./docs/getting_started.md):** Covers initial project setup and logging in.
*   **[API Documentation](./docs/api/index.md):** Detailed reference for all available API endpoints.
*   **[Admin Usage Guide](./docs/admin_guide.md):** Guide for using the CMS Admin interface.
*   **[Docker Usage Guide](./docs/docker_usage.md):** Instructions for running the project with Docker.

## Disclaimer: AI-Assisted Development

Please be advised that the development of the Lithographer CMS framework involved significant assistance from generative AI, specifically large language models (LLMs) from Google (Gemini) and an AI Agent.

Throughout the development process, AI assistance was utilized for various tasks, including but not limited to:

* Developing & Tunning initial prompts based on requirement specifications.
* Producing boilerplate code snippets for models, APIs, admin interfaces, and other components based on detailed prompts.
* Creating configuration files (e.g., `Dockerfile`, `docker-compose.yml`).
* Drafting documentation sections (e.g., API documentation, feature descriptions).
* Providing suggestions on architecture, implementation approaches, and best practices.

It is crucial to understand that all AI-generated outputs served as a starting point or accelerator. This code, configuration, documentation, and architectural decision are going thorough review & testing by the me. I am providing this code for developer to play around. This code si strickly not for proudction as I am yet unsure of its security related aspects. 

We believe in transparency regarding the tools and methodologies used in our development process.