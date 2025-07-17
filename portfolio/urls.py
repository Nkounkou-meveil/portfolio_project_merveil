# portfolio/urls.py
from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Page principale
    path('', views.index, name='index'),
    
    # Pages détaillées
    path('projet/<slug:slug>/', views.projet_detail, name='projet_detail'),
    path('galerie/<slug:slug>/', views.galerie_detail, name='galerie_detail'),
    
    # Pages de listing complet
    path('projets/', views.tous_projets, name='tous_projets'),
    path('galerie/', views.toute_galerie, name='toute_galerie'),
    
    # AJAX endpoints
    path('newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('contact/', views.contact_message, name='contact_message'),
    
    # Newsletter unsubscribe
    path('newsletter/unsubscribe/<uuid:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    # Recherche
    path('search/', views.search, name='search'),
    
    # API endpoints (pour AJAX)
    path('api/projects/', views.api_projects, name='api_projects'),
    path('api/gallery/', views.api_gallery, name='api_gallery'),
    path('api/feed/', views.api_feed, name='api_feed'),
]

# portfolio_project/urls.py (URLs principales du projet)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""