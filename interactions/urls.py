from django.urls import path
from . import views

urlpatterns = [
    path('ajouter/<str:type_obj>/<int:obj_id>/', views.ajouter_commentaire, name='ajouter_commentaire'),
    path('vote/<int:comm_id>/<str:action>/', views.vote_commentaire, name='vote_commentaire'),
    path('supprimer/<int:comm_id>/', views.supprimer_commentaire, name='supprimer_commentaire'),
    path('filiere/<int:filiere_id>/favori/', views.toggle_favori, name='toggle_favori'),
    path('voir_profil/<str:username>/', views.voir_profil, name='voir_profil'),
    path('notification/lire/<int:notif_id>/', views.marquer_comme_lu, name='marquer_comme_lu'),
    path('notification/archiver/<int:notif_id>/', views.archiver_notification, name='archiver_notification'),
]