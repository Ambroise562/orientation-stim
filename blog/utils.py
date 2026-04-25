def calculer_moyenne_classement_pure(serie_nom, notes_dict, univ_nom, ecole_nom, filiere_nom):
    """
    serie_nom: str (ex: 'C')
    notes_dict: dict { 'Mathématiques': 16, 'Physique-Chimie-Technologie': 14, ... }
    """
    from .models import Serie, CoefficientSerie, RegleAdmission, Filiere

    try:
        # 1. Identification de la filière et de la série
        filiere_obj = Filiere.objects.get(
            nom=filiere_nom,
            ecole__nom=ecole_nom,
            ecole__universite__nom=univ_nom
        )
        serie_obj = Serie.objects.get(nom=serie_nom)
        
        # 2. Récupération de la règle d'admission (qui définit les matières concernées)
        regle = RegleAdmission.objects.get(filiere=filiere_obj, serie=serie_obj)
        disciplines_concernees = regle.matieres_poids.all()
        
    except (Filiere.DoesNotExist, Serie.DoesNotExist, RegleAdmission.DoesNotExist):
        return {"erreur": "Configuration introuvable pour ce couple Filière/Série."}

    points_total = 0
    somme_coefficients = 0
    details_calcul = []

    # 3. Boucle sur les matières concernées par la filière
    for discipline in disciplines_concernees:
        # On récupère le coefficient OFFICIEL de cette discipline pour cette série
        try:
            coef_obj = CoefficientSerie.objects.get(discipline=discipline, serie=serie_obj)
            coefficient = coef_obj.valeur if coef_obj.valeur is not None else 0
        except CoefficientSerie.DoesNotExist:
            # Sécurité si le coefficient n'est pas renseigné en base
            continue

        # On récupère la note saisie par l'utilisateur
        note = notes_dict.get(discipline.nom, 0)
        if note is None:
            note = 0
        
        # Calcul des points
        points_total += (note * coefficient)
        somme_coefficients += coefficient
        
        details_calcul.append({
            "matiere": discipline.nom,
            "note": note,
            "coefficient": coefficient
        })

    # 4. Calcul final
    if somme_coefficients == 0:
        return {"erreur": "Aucun coefficient valide trouvé pour les matières de cette filière."}

    moyenne_classement = points_total / somme_coefficients

    return {
        "filiere": filiere_nom,
        "moyenne_classement": round(moyenne_classement, 3),
        "details": details_calcul,
        "total_coefficients": somme_coefficients
    }