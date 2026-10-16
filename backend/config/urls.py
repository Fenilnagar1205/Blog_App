from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # 1. इस URL पर username और password भेजकर Token मिलेगा (Login)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # 2. इस URL पर Refresh Token भेजकर नया Access Token मिलेगा
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("blogs/", include("blogs.urls")),
    path("blogs/", include("interactions.urls")),
    path("accounts/", include("accounts.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
