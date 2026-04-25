# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages # Import indispensable pour les alertes
from .forms import InscriptionForm
from django.contrib.auth.decorators import login_required
from .forms import ProfilUpdateForm, UserUpdateForm
from interactions.models import Favori, Commentaire # Importe tes modèles

def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # Message flash de succès
            messages.success(request, f'Félicitations {username}, votre compte a été créé avec succès ! Connectez-vous.')
            return redirect('login')
        else:
            # Si le formulaire n'est pas valide (ex: mot de passe trop simple)
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations saisies.")
    else:
        form = InscriptionForm()
    
    return render(request, 'inscription.html', {'form': form})


@login_required
def modifier_profil(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilUpdateForm(request.POST, request.FILES, instance=request.user.profil)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('modifier_profil')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilUpdateForm(instance=request.user.profil)

    return render(request, 'modifier_profil.html', {
        'u_form': u_form,
        'p_form': p_form
    })


@login_required
def profil_view(request):
    # 1. Récupérer les filières favorites de l'utilisateur
    favoris = Favori.objects.filter(user=request.user).select_related('filiere', 'filiere__ecole')

    # 2. Récupérer les dernières interactions (Commentaires)
    mes_interactions = Commentaire.objects.filter(auteur=request.user).select_related('ecole', 'filiere').order_by('-date_pub')

    # 3. Récupérer l'historique complet des notifications
    # On récupère toutes les notifications (lues et non lues) classées par date
    mes_notifications = request.user.notifications.filter(est_archivee=False).order_by('-date_creation')
    context = {
        'favoris': favoris,
        'mes_interactions': mes_interactions,
        'mes_notifications': mes_notifications,  # Ajout au contexte
    }
    return render(request, 'profil.html', context)


