from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import escape
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .utils import *
from django.conf import settings

def get_safe_referrer(request):
    """Validate and return a safe redirect URL"""
    referrer = request.META.get('HTTP_REFERER', '/')
    # Only allow internal redirects
    if referrer and (referrer.startswith('/') or referrer.startswith('http')):
        from urllib.parse import urlparse
        parsed = urlparse(referrer)
        # Ensure the referrer is from the same domain
        if parsed.netloc in ['', request.get_host()]:
            return referrer
    return '/'


# Create your views here.
def home(request):
    return render(request, 'home.html')

def universites(request):
    universites_list = Universite.objects.prefetch_related('ecoles').all()
    paginator = Paginator(universites_list, settings.PAGINATION_LIMIT)
    page = request.GET.get('page')
    try:
        universites = paginator.page(page)
    except PageNotAnInteger:
        universites = paginator.page(1)
    except EmptyPage:
        universites = paginator.page(paginator.num_pages)
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
    ecole = get_object_or_404(Ecole.objects.select_related('universite'), id=ecole_id)
    filieres = ecole.filieres.all().prefetch_related('series_autorisees', 'matieres_principales', 'admission', 'commentaires__auteur')  # Grâce à related_name='filieres'
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
    
    if query and len(query) >= 2:  # Limit queries shorter than 2 characters
        query_limit = getattr(settings, 'SEARCH_RESULT_LIMIT', 100)
        
        # 1. Recherche dans les Écoles (Nom, Nom détaillé, Description)
        ecoles_list = Ecole.objects.filter(
            Q(nom__icontains=query) | 
            Q(nom_detaille__icontains=query) | 
            Q(description__icontains=query)
        ).select_related('universite').distinct()[:query_limit]

        # 2. Recherche dans les Filières (Nom, Débouchés)
        filieres_list = Filiere.objects.filter(
            Q(nom__icontains=query) | 
            Q(debouches__icontains=query) 
        ).select_related('ecole').distinct()[:query_limit]
        
        # Apply pagination
        page_num = request.GET.get('page', 1)
        paginator_ecoles = Paginator(ecoles_list, 10)
        paginator_filieres = Paginator(filieres_list, 10)
        
        try:
            ecoles = paginator_ecoles.page(page_num)
            filieres = paginator_filieres.page(page_num)
        except (PageNotAnInteger, EmptyPage):
            ecoles = paginator_ecoles.page(1)
            filieres = paginator_filieres.page(1)

    return render(request, 'recherche.html', {
        'ecoles': ecoles,
        'filieres': filieres,
        'query': query
    })



    
from django.contrib.auth.decorators import login_required

def future_universites_privees(request):
    return render(request, 'future.html')


def aide_view(request):
    return render(request, 'aide.html')


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

