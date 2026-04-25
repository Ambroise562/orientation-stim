from django.db.models import Q
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .utils import *


# Create your views here.
def home(request):
    return render(request, 'home.html')

def universites(request):
    universites = Universite.objects.all()
    return render(request, 'universites.html', {'universites': universites})



def detail_universite(request, univ_id):
    # On récupère l'université ou on affiche une erreur 404 si elle n'existe pas
    universite = get_object_or_404(Universite, id=univ_id)
    
    # Grâce à related_name='ecoles', on récupère toutes les écoles liées
    ecoles = universite.ecoles.all()
    
    return render(request, 'detail_universite.html', {
        'universite': universite,
        'ecoles': ecoles
    })
    
def detail_ecole(request, ecole_id):
    ecole = get_object_or_404(Ecole, id=ecole_id)
    filieres = ecole.filieres.all().prefetch_related('series_autorisees', 'matieres_principales', 'admission')  # Grâce à related_name='filieres'
    user_favoris_ids = []
    if request.user.is_authenticated:
        user_favoris_ids = request.user.favoris.values_list('filiere_id', flat=True)
    return render(request, 'ecole_detail.html', {
        'ecole': ecole,
        'filieres': filieres,
        'user_favoris_ids': user_favoris_ids,
    })
    

def recherche_globale(request):
    query = request.GET.get('q', '').strip()
    ecoles = []
    filieres = []
    
    if query:
        # 1. Recherche dans les Écoles (Nom, Nom détaillé, Description)
        ecoles = Ecole.objects.filter(
            Q(nom__icontains=query) | 
            Q(nom_detaille__icontains=query) | 
            Q(description__icontains=query)
        ).distinct()

        # 2. Recherche dans les Filières (Nom, Débouchés) 
        # + Recherche par Série (si la requête correspond au nom d'une série)
        filieres = Filiere.objects.filter(
            Q(nom__icontains=query) | 
            Q(debouches__icontains=query) 
            ).select_related('ecole').distinct()

    return render(request, 'recherche.html', {
        'ecoles': ecoles,
        'filieres': filieres,
        'query': query
    })



    
from django.contrib.auth.decorators import login_required

def simulateur_view(request):
    # 1. Gestion des données initiales (Lien avec le Profil)
    initial_data = {}
    serie_choisie_obj = None
    
    if request.user.is_authenticated:
        profil = request.user.profil
        if profil.serie:
            initial_data['serie'] = profil.serie
            serie_choisie_obj = profil.serie

    # 2. Initialisation du formulaire
    if request.method == "POST":
        form = SimulateurForm(request.POST)
    else:
        form = SimulateurForm(initial=initial_data)

    # 3. Préparation de la configuration JavaScript (Matitères par Série)
    regles_all = RegleAdmission.objects.select_related('serie').prefetch_related('matieres_poids').all()
    
    config_js = {}
    for regle in regles_all:
        s_id = str(regle.serie.id)
        if s_id not in config_js:
            config_js[s_id] = set()
        
        for discipline in regle.matieres_poids.all():
            config_js[s_id].add(f"note_{discipline.id}")
    
    # Conversion des sets en listes pour JSON
    config_js = {s_id: list(fields) for s_id, fields in config_js.items()}

    # 4. Traitement du calcul après soumission
    resultats_orientation = []
    
    if request.method == "POST" and form.is_valid():
        serie_choisie_obj = form.cleaned_data['serie']
        regles_compatibles = RegleAdmission.objects.filter(
            serie=serie_choisie_obj
        ).select_related('filiere', 'filiere__ecole__universite')

        for regle in regles_compatibles:
            notes_dict = {}
            for d in regle.matieres_poids.all():
                valeur_note = form.cleaned_data.get(f'note_{d.id}', 0)
                notes_dict[d.nom] = valeur_note if valeur_note is not None else 0
            
            # Appel de ta fonction de calcul
            res = calculer_moyenne_classement_pure(
                serie_choisie_obj.nom, 
                notes_dict, 
                regle.filiere.ecole.universite.nom, 
                regle.filiere.ecole.nom, 
                regle.filiere.nom
            )
            
            if "erreur" not in res:
                res['obj_filiere'] = regle.filiere
                resultats_orientation.append(res)

        # Tri par moyenne décroissante
        resultats_orientation = sorted(
            resultats_orientation, 
            key=lambda x: x['moyenne_classement'], 
            reverse=True
        )

    # 5. Extraction des écoles uniques pour les filtres du template
    ecoles = set([res['obj_filiere'].ecole.nom for res in resultats_orientation if 'obj_filiere' in res])

    context = {
        'form': form,
        'config_js': config_js,
        'resultats': resultats_orientation,
        'ecoles': ecoles,
        'serie_choisie': serie_choisie_obj, # Objet série pour le titre HTML
    }
    
    return render(request, 'simulateur.html', context)  

