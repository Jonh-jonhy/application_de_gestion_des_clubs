# gestion_clubs/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Toutes les routes auth seront préfixées par /api/auth/
    path('api/auth/', include('accounts.urls')),
]

# Permet de servir les fichiers médias en développement (photos, logos)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)