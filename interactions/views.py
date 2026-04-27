from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Commentaire , Favori, Notification
from blog.models import Ecole, Filiere
from django.contrib.auth.models import User

@login_required
def ajouter_commentaire(request, type_obj, obj_id):
    if request.method == "POST":
        contenu = request.POST.get('contenu')
        parent_id = request.POST.get('parent_id')
        
        nouveau_comm = Commentaire(
            auteur=request.user,
            contenu=contenu
        )

        # Liaison à l'objet (Ecole ou Filiere)
        if type_obj == 'ecole':
            nouveau_comm.ecole = get_object_or_404(Ecole, id=obj_id)
        elif type_obj == 'filiere':
            nouveau_comm.filiere = get_object_or_404(Filiere, id=obj_id)

        if parent_id:
            parent_comm = get_object_or_404(Commentaire, id=parent_id)
            nouveau_comm.parent = parent_comm
            
        nouveau_comm.save() 
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def vote_commentaire(request, comm_id, action):
    commentaire = get_object_or_404(Commentaire, id=comm_id)
    user = request.user
    
    if action == 'like':
        if user in commentaire.likes.all():
            commentaire.likes.remove(user)
        else:
            commentaire.likes.add(user)
            commentaire.dislikes.remove(user) # On ne peut pas liker ET disliker
            
    elif action == 'dislike':
        if user in commentaire.dislikes.all():
            commentaire.dislikes.remove(user)
        else:
            commentaire.dislikes.add(user)
            commentaire.likes.remove(user)

    return JsonResponse({
        'score': commentaire.score,
        'likes': commentaire.likes.count(),
        'dislikes': commentaire.dislikes.count(),
    })
    
from django.contrib import messages

@login_required
def supprimer_commentaire(request, comm_id):
    # Récupère le commentaire (que ce soit un parent ou une réponse)
    commentaire = get_object_or_404(Commentaire, id=comm_id)
    
    # Vérification STRICTE de propriété
    if request.user == commentaire.auteur or request.user.is_staff:
        
        # Cas 1 : C'est une réponse OU un parent sans enfant -> On supprime vraiment
        if commentaire.parent or not commentaire.reponses.exists():
            commentaire.delete()
            messages.success(request, "Votre message a été supprimé.")
        
        # Cas 2 : C'est un parent qui a des réponses -> On vide juste le texte
        else:
            commentaire.contenu = "Ce message a été supprimé par son auteur."
            # On peut aussi changer l'auteur en un compte "Système" si besoin
            commentaire.save()
            messages.info(request, "Le contenu du message a été retiré.")
            
    else:
        # Tentative de suppression illégale (ex: par l'auteur du commentaire parent)
        messages.error(request, "Action interdite : vous n'êtes pas l'auteur de ce message.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
        
@login_required
def ajouter_favori(request, filiere_id):
    filiere = get_object_or_404(Filiere, id=filiere_id)
    favori, created = Favori.objects.get_or_create(user=request.user, filiere=filiere)
    
    if not created:
        favori.delete() # Si le favori existe déjà, on le supprime (toggle)
        
    return redirect(request.META.get('HTTP_REFERER', '/'))


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Favori, Filiere

@login_required
def toggle_favori(request, filiere_id):
    filiere = get_object_or_404(Filiere, id=filiere_id)
    favori, created = Favori.objects.get_or_create(user=request.user, filiere=filiere)
    
    is_favori = True
    if not created:
        favori.delete()
        is_favori = False
    
    # CRITIQUE : Cette réponse doit correspondre aux clés du script JS
    return JsonResponse({
        'is_favori': is_favori,
        'filiere_id': filiere_id
    })
    
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def voir_profil(request, username):
    # On récupère l'aîné en question
    aine = get_object_or_404(User, username=username)
    return render(request, 'profil_public.html', {'aine': aine})


# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Commentaire, Notification

@receiver(post_save, sender=Commentaire, dispatch_uid="unique_notifier_reponse_signal")
def notifier_reponse(sender, instance, created, **kwargs):
    if created and instance.parent:
        if instance.parent.auteur != instance.auteur:
            
            url_cible = "/"
            
            # Cas 1 : Le commentaire concerne une ÉCOLE
            # On redirige vers la page de l'Université parente
            if instance.ecole:
                # On récupère l'ID de l'université via la relation dans ton modèle Ecole
                univ_id = instance.ecole.universite.id 
                url_cible = f"/universite/{univ_id}/#comment-{instance.id}"
            
            # Cas 2 : Le commentaire concerne une FILIÈRE
            # On redirige vers la page de l'École parente
            elif instance.filiere:
                # On récupère l'ID de l'école via la relation dans ton modèle Filiere
                ecole_id = instance.filiere.ecole.id
                url_cible = f"/ecole/{ecole_id}/#comment-{instance.id}"

            # Création de la notification
            Notification.objects.create(
                destinataire=instance.parent.auteur,
                acteur=instance.auteur,
                message=f"{instance.auteur.username} a répondu à votre échange.",
                url_cible=url_cible
            )     
            
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def marquer_comme_lu(request, notif_id):
    # On récupère la notification appartenant à l'utilisateur
    notification = get_object_or_404(Notification, id=notif_id, destinataire=request.user)
    
    # On la marque comme lue
    notification.est_lu = True
    notification.save()
    
    # On redirige vers l'URL cible (la page du commentaire)
    if notification.url_cible:
        return redirect(notification.url_cible)
    return redirect('/') # Repli au cas ou
    
@login_required
def archiver_notification(request, notif_id):
    # On récupère la notif, on la passe en 'archivée' et on sauvegarde
    notification = get_object_or_404(request.user.notifications, id=notif_id)
    notification.est_archivee = True
    notification.save()
    return redirect('profil')