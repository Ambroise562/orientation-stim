from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.html import escape
from django.core.exceptions import ValidationError
from .models import Commentaire , Favori, Notification
from blog.models import Ecole, Filiere
from django.contrib.auth.models import User
from urllib.parse import urlparse


def get_safe_referrer(request):
    """Validate and return a safe redirect URL"""
    referrer = request.META.get('HTTP_REFERER', '/')
    if referrer:
        parsed = urlparse(referrer)
        # Only allow internal redirects (same domain)
        if parsed.netloc in ['', request.get_host()] or parsed.netloc.startswith(request.get_host()):
            if referrer.startswith('/') or referrer.startswith('http'):
                return referrer
    return '/' 


@login_required
def admin_dashboard(request):
    # Accès réservé aux admins (staff/superuser)
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/')

    from django.contrib.auth.models import User
    from django.db.models import Count

    total_users = User.objects.count()
    total_commentaires = Commentaire.objects.count()

    # Séparer les utilisateurs par rôle
    utilisateurs_superuser = User.objects.filter(is_superuser=True).select_related('profil').order_by('-date_joined')
    utilisateurs_staff = User.objects.filter(is_staff=True, is_superuser=False).select_related('profil').order_by('-date_joined')
    utilisateurs_simples = User.objects.filter(is_staff=False, is_superuser=False).select_related('profil').order_by('-date_joined')

    # 50 derniers commentaires (parents + réponses)
    derniers_commentaires = (
        Commentaire.objects
        .select_related('auteur', 'ecole', 'filiere', 'parent', 'auteur__profil')
        .order_by('-date_pub')[:50]
    )


    # Favoris: top par filière, sans afficher les IDs dans le template.
    # On expose l'école associée pour rendre un lien.
    favoris_par_filiere = (
        Favori.objects
        .values('filiere_id', 'filiere__nom', 'filiere__ecole_id')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    favoris_par_filiere = list(favoris_par_filiere[:30])
    total_favoris = Favori.objects.count()

    total_notifications = Notification.objects.count()
    notifications_non_lues = Notification.objects.filter(est_lu=False).count()
    notifications_archivees = Notification.objects.filter(est_archivee=True).count()

    context = {
        'utilisateurs_superuser': utilisateurs_superuser,
        'utilisateurs_staff': utilisateurs_staff,
        'utilisateurs_simples': utilisateurs_simples,
        'total_users': total_users,
        'total_commentaires': total_commentaires,
        'derniers_commentaires': derniers_commentaires,
        'favoris_par_filiere': favoris_par_filiere,
        'total_favoris': total_favoris,
        'total_notifications': total_notifications,
        'notifications_non_lues': notifications_non_lues,
        'notifications_archivees': notifications_archivees,
    }

    return render(request, 'admin_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def ajouter_commentaire(request, type_obj, obj_id):

    contenu = request.POST.get('contenu', '').strip()
    parent_id = request.POST.get('parent_id')
    
    # Validate comment content
    if not contenu:
        from django.contrib import messages
        messages.error(request, "Le commentaire ne peut pas être vide.")
        return redirect(get_safe_referrer(request))
    
    if len(contenu) > 5000:
        from django.contrib import messages
        messages.error(request, "Le commentaire est trop long (max 5000 caractères).")
        return redirect(get_safe_referrer(request))
    
    # Sanitize content (escape HTML)
    contenu = escape(contenu)
    
    nouveau_comm = Commentaire(
        auteur=request.user,
        contenu=contenu
    )

    # Liaison à l'objet (Ecole ou Filiere)
    try:
        if type_obj == 'ecole':
            nouveau_comm.ecole = get_object_or_404(Ecole, id=obj_id)
        elif type_obj == 'filiere':
            nouveau_comm.filiere = get_object_or_404(Filiere, id=obj_id)
        else:
            raise ValidationError("Type d'objet invalide")
    except ValidationError:
        from django.contrib import messages
        messages.error(request, "Type d'objet invalide.")
        return redirect(get_safe_referrer(request))

    if parent_id:
        parent_comm = get_object_or_404(Commentaire, id=parent_id)
        nouveau_comm.parent = parent_comm
        
    nouveau_comm.save() 
    
    from django.contrib import messages
    messages.success(request, "Votre commentaire a été ajouté.")
    return redirect(get_safe_referrer(request))

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
    return redirect(get_safe_referrer(request))
        
@login_required
def ajouter_favori(request, filiere_id):
    filiere = get_object_or_404(Filiere, id=filiere_id)
    favori, created = Favori.objects.get_or_create(user=request.user, filiere=filiere)
    
    if not created:
        favori.delete() # Si le favori existe déjà, on le supprime (toggle)
        
    return redirect(get_safe_referrer(request))


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
    return redirect(get_safe_referrer(request))