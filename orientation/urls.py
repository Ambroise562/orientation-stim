"""
URL configuration for second project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from blog.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('universites/', universites, name='universites'),  # type: ignore
    path('universite/<int:univ_id>/', detail_universite, name='detail_universite'), # type: ignore
    path('ecole/<int:ecole_id>/', detail_ecole, name='detail_ecole'), # type: ignore
    path('simulateur', simulateur_view, name='simulateur'), # type: ignore
    path('recherche_globale', recherche_globale, name='recherche_globale'), # type: ignore
    
    
    # On inclut les URLs de l'app 'comptes'
    # Toutes les adresses de comptes commenceront par /comptes/
    path('comptes/', include('comptes.urls')),
    path('interactions/', include('interactions.urls'))



]

# On ajoute cette ligne pour que Django affiche les images en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)