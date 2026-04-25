from django.db import models
from django.contrib.auth.models import User
from blog.models import Serie 
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profil(models.Model):
    # Définition des rôles
    TYPE_CHOICES = [
        ('BACHELIER', 'Nouveau Bachelier (En quête d\'orientation)'),
        ('AINE', 'Aîné / Étudiant (Partage d\'expérience)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    
    # Nouveau champ pour différencier les deux types
    type_utilisateur = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='BACHELIER',
        verbose_name="Qui êtes-vous ?"
    )
    
    serie = models.ForeignKey(Serie, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Champ spécifique pour les aînés
    etablissement = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name="Université ou École (pour les aînés)"
    )
    
    bio = models.TextField(max_length=300, blank=True, verbose_name="Ma présentation")
    photo = models.ImageField(upload_to='profils/', default='profils/default.png')
    
    def __str__(self):
        return f"{self.user.username} ({self.get_type_utilisateur_display()})"

# Tes signaux restent identiques (ils fonctionnent très bien)
@receiver(post_save, sender=User)
def gerer_profil_utilisateur(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
    # On utilise hasattr pour éviter l'erreur si le profil n'existe pas encore lors d'une sauvegarde
    if hasattr(instance, 'profil'):
        instance.profil.save()