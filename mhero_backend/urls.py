from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, re_path
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from lib.swagger_utils import BothHttpAndHttpsSchemaGenerator

urlpatterns = [
    path('health/', include('health_check.urls')),
    path("v1/accounts/", include("accounts.urls")),
    path("v1/payments/", include("payments.urls")),
    path("v1/insights/", include("insights.urls")),
]

api_info = openapi.Info(
    title="Auth API",
    default_version="v1",
)
# public=False and permissions=[AllowAny] let everyone visit swagger pages but view limited
# endpoints, to see all endpoints user should be authorized (see SWAGGER_SETTINGS)
schema_view = get_schema_view(
    info=api_info,
    public=False,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=[AllowAny],
)

urlpatterns += [
    re_path(
        r"^v1/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json-yaml",
    ),
    path(
        "v1/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "v1/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# TODO change back with production
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
