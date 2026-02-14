"""
URL configuration for authentic_place project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🔐 Admin Django
    path('admin/', admin.site.urls),

    # 🏠 Application principale (market)
    # Gère : / , /login, /register, /dashboard, /product/, etc.
    path('', include('market.urls')),

    # 📄 Pages statiques (si nécessaire)
    path('', include('pages.urls')),

    # 🔑 Auth Django (mot de passe oublié, reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]

# 🖼️ Media en développement uniquement
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
