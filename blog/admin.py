# Register your models here.

from django.contrib import admin
from .models import *
from django import forms
# Configuration simple pour les paramètres de base

admin.site.register(Serie)
admin.site.register(Admission)
admin.site.register(RegleAdmission)



class RegleAdmissionInline(admin.TabularInline):
    model = RegleAdmission
    extra = 1
    # Le 'filter_horizontal' fonctionne même à l'intérieur d'un tableau !
    filter_horizontal = ('matieres_poids',)

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', )
    search_fields = ('nom',)
    

@admin.register(CoefficientSerie)
class CoefficientSerieAdmin(admin.ModelAdmin):
    # Ce qui s'affiche dans les colonnes du tableau
    list_display = ('discipline', 'serie', 'valeur')
    
    # Pour filtrer rapidement par Série (ex: voir seulement le Bac C) ou par Discipline
    list_filter = ('serie', 'discipline')
    
    # LE TRUC MAGIQUE : Permet de modifier le chiffre du coef sans cliquer sur la fiche !
    list_editable = ('valeur',)
    
    # Pour chercher une matière précise rapidement
    search_fields = ('discipline__nom', 'serie__nom')

@admin.register(Universite)
class UniversiteAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste des universités
    list_display = ('nom', 'nom_complet', 'localisation')
    search_fields = ('nom', 'nom_complet')

@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'universite', 'created_at')
    # Permet de filtrer par université dans la colonne de droite
    list_filter = ('universite','nom_detaille')
    search_fields = ('nom', 'nom_detaille')

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ecole', 'bourses', 'aides_universitaires')
    # Filtres pratiques pour retrouver une filière rapidement
    list_filter = ('ecole__universite', 'ecole', 'admission')
    search_fields = ('nom', 'bourses', 'aides_universitaires')
    
    # INTERFACE DE SÉLECTION HORIZONTALE
    # Très important pour choisir les séries et matières sans rester appuyé sur Ctrl
    filter_horizontal = ('series_autorisees', 'matieres_principales', 'admission')
    inlines = [RegleAdmissionInline]
    
    # Organisation par sections dans le formulaire de saisie
    fieldsets = (
        ('Informations Générales', {
            'fields': ('ecole', 'nom', 'debouches')
        }),
        ('Critères d\'Admission', {
            'fields': ('series_autorisees', 'matieres_principales', 'admission')
        }),
        ('Avantages Étudiants', {
            'fields': ('bourses', 'aides_universitaires')
        }),
    )