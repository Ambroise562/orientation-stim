# comptes/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    # Inscription (ta vue personnalisée)
    path('profil/',profil_view, name='profil'),
    path('inscription/', inscription_view, name='inscription'),
    
    # Connexion (vue intégrée de Django avec ton template)
    path('connexion/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Déconnexion (vue intégrée)
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('profil/modifier/', modifier_profil, name='modifier_profil'),
    

    
    path('modifier-mot-de-passe/', 
         auth_views.PasswordChangeView.as_view(template_name='password_change.html'), 
         name='password_change'),
         
    path('mot-de-passe-modifie/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), 
         name='password_change_done'),

    # 1. Demande de réinitialisation (Saisie de l'email)
    path('mot-de-passe-oublie/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),

    # 2. Confirmation d'envoi du mail
    path('mot-de-passe-oublie/envoye/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    # 3. Lien reçu par email (Saisie du nouveau mot de passe)
    path('reinitialiser/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),

    # 4. Message final de succès
    path('reinitialiser/termine/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),

]