from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from photo_app.views import process_integration

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', process_integration),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
