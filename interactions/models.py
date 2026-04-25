from django.db import models
from django.contrib.auth.models import User
from blog.models import Ecole, Filiere 

class Commentaire(models.Model):
    # Liens optionnels vers les deux entités
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True, related_name='commentaires')
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, null=True, blank=True, related_name='commentaires')
    
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_pub = models.DateTimeField(auto_now_add=True)
    
    # Pour répondre à un commentaire précis
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='reponses')
    
    # Système de votes (M2M vers User)
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True)

    class Meta:
        ordering = ['-date_pub'] # Les plus récents en premier

    def __str__(self):
        return f"Par {self.auteur.username} le {self.date_pub.strftime('%d/%m/%Y')}"

    @property
    def est_une_reponse(self):
        return self.parent is not None

    @property
    def score(self):
        return self.likes.count() - self.dislikes.count()
    
# interactions/models.py
class Favori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'filiere') # Un utilisateur ne peut liker qu'une fois la même filière
        
        
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    acteur = models.ForeignKey(User, on_delete=models.CASCADE) # Celui qui a répondu
    message = models.CharField(max_length=255)
    url_cible = models.CharField(max_length=255, blank=True, null=True) # Pour cliquer et aller au commentaire
    est_lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_archivee = models.BooleanField(default=False)
    class Meta:
        ordering = ['-date_creation']