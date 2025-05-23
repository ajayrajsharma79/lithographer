"""
URL configuration for lithographer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse # Import HttpResponse
from django.views.generic import TemplateView # For simple static views if needed
from graphene_django.views import GraphQLView # For GraphQL endpoint

# API Router Setup (DRF)
from rest_framework.routers import DefaultRouter
# Import ViewSets
from apps.core.views import LanguageViewSet, SystemSettingViewSet
from apps.users.views import RoleViewSet, CMSUserViewSet, APIKeyViewSet
# Import specific frontend views instead of the ViewSet
from apps.frontend_users.views import UserRegistrationView, UserProfileView #, password_reset_request, password_reset_confirm
from apps.webhooks.views import WebhookEndpointViewSet, WebhookEventLogViewSet
# Import media viewsets
from apps.media.views import FolderViewSet, MediaTagViewSet, MediaAssetViewSet, ImageOptimizationProfileViewSet
# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
# Import content viewsets
from apps.content.views import (
    ContentTypeViewSet, TaxonomyViewSet, TermViewSet,
    ContentInstanceViewSet, ContentVersionViewSet
)
# Import comment views
from apps.comments.views import CommentCreateView #, CommentListView
# Import component viewsets
from apps.components.views import ComponentDefinitionViewSet

# Create a router and register our viewsets.
router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language') # Use basename as lookup is 'code'
router.register(r'system-settings', SystemSettingViewSet, basename='systemsetting') # Use basename for singleton ViewSet
# router.register(r'permissions', PermissionViewSet) # Removed registration
router.register(r'roles', RoleViewSet)
router.register(r'api-keys', APIKeyViewSet, basename='apikey') # Add basename
router.register(r'cms-users', CMSUserViewSet)
# router.register(r'frontend-users', FrontEndUserViewSet) # Replaced by specific auth views
router.register(r'webhook-endpoints', WebhookEndpointViewSet, basename='webhookendpoint')
router.register(r'webhook-logs', WebhookEventLogViewSet) # Read-only logs
# Register content viewsets
router.register(r'content-types', ContentTypeViewSet, basename='contenttype') # Use basename as lookup is api_id
router.register(r'taxonomies', TaxonomyViewSet, basename='taxonomy') # Use basename as lookup is api_id
router.register(r'terms', TermViewSet, basename='term') # Terms might need filtering by taxonomy in practice
router.register(r'content-instances', ContentInstanceViewSet, basename='contentinstance')
router.register(r'content-versions', ContentVersionViewSet, basename='contentversion') # Add basename for read-only
# Register media viewsets
router.register(r'media/folders', FolderViewSet)
router.register(r'media/tags', MediaTagViewSet, basename='mediatag') # Use basename as lookup is slug
router.register(r'media/assets', MediaAssetViewSet)
router.register(r'media/optimization-profiles', ImageOptimizationProfileViewSet)
# Register component viewsets
router.register(r'component-definitions', ComponentDefinitionViewSet, basename='componentdefinition') # Use basename as lookup is api_id


# Nested routing for terms (Manual approach - consider drf-nested-routers for complex cases)
# This pattern allows /taxonomies/{taxonomy_api_id}/terms/
taxonomy_terms_list = TermViewSet.as_view({'get': 'list', 'post': 'create'})
taxonomy_terms_detail = TermViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})


urlpatterns = [
    # Add nested term routes BEFORE the main router include
    path('api/v1/taxonomies/<str:taxonomy_api_id>/terms/', taxonomy_terms_list, name='taxonomy-terms-list'),
    path('api/v1/taxonomies/<str:taxonomy_api_id>/terms/<uuid:pk>/', taxonomy_terms_detail, name='taxonomy-terms-detail'),
    # Nested comment routes
    path('api/v1/content-instances/<uuid:instance_pk>/comments/', CommentCreateView.as_view(), name='comment-create'), # POST only
    # path('api/v1/content-instances/<uuid:instance_pk>/comments/', CommentListView.as_view(), name='comment-list'), # GET only - Use query param on instance detail instead?
    # Django Admin
    path('admin/', admin.site.urls),

    # API Endpoints (Router - includes CMS users, content, media etc.)
    path('api/v1/', include(router.urls)),

    # Specific Auth Endpoints for FrontEnd Users (JWT)
    path('api/auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # JWT Login
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
    # path('api/auth/password/reset/', password_reset_request, name='password_reset_request'),
    # path('api/auth/password/reset/confirm/', password_reset_confirm, name='password_reset_confirm'),

    # path('api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')), # Removed - Use JWT endpoints above

    # GraphQL Endpoint
    path("graphql", GraphQLView.as_view(graphiql=settings.DEBUG)), # Enable GraphiQL interface in DEBUG mode

    # App-specific URLs (Include these as apps are developed)
    # path('users/', include('apps.users.urls')),
    # path('frontend/', include('apps.frontend_users.urls')),
    # path('media/', include('apps.media.urls')),
    # path('comments/', include('apps.comments.urls')),
    # path('webhooks/', include('apps.webhooks.urls')),
    # path('layouts/', include('apps.layouts.urls')),
    # path('', include('apps.content.urls')), # Example: Content app handles root

    # Simple health check endpoint
    path('health/', lambda request: HttpResponse("OK"), name='health_check'),

    # Example: Serve a simple homepage if needed directly from root urls
    # path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Add a simple root view
    path('', lambda request: HttpResponse("<h1>Lithographer CMS Root</h1><p>API available at /api/v1/</p><p>Admin available at /admin/</p>"), name='root'),
]

# Serve static and media files during development
if settings.DEBUG:
    # HttpResponse already imported at top level
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add debug toolbar URLs if installed
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin Site Customization
admin.site.site_header = "Lithographer CMS Administration"
admin.site.site_title = "Lithographer CMS Admin"
admin.site.index_title = "Welcome to Lithographer CMS"
