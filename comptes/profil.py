from django.contrib.auth.models import User
from comptes.models import Profil

# On parcourt tous les utilisateurs
for user in User.objects.all():
    # Si l'utilisateur n'a pas de profil, on le crée
    if not hasattr(user, 'profil'):
        Profil.objects.create(user=user)
        print(f"Profil créé pour {user.username}")