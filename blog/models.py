from django.db import models


# --- Classes de base (Paramètres) ---
class Discipline(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nom

class Serie(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nom

class CoefficientSerie(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='coefficients')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, related_name='coefficients')
    valeur = models.PositiveIntegerField(help_text="Le coefficient officiel au Bénin pour cette série")

    class Meta:
        unique_together = ('discipline', 'serie')
        verbose_name = "Coefficient par Série"

    def __str__(self):
        return f"{self.discipline.nom} en Série {self.serie.nom} : Coef {self.valeur}"

class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nom

class Admission(models.Model):
    nom = models.CharField(max_length=100)
    def __str__(self):
        return self.nom
    


# --- Classes Principales ---

class Universite(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    nom_complet = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='universites/logos/')
    description = models.TextField()
    localisation = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = "Université"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Ecole(models.Model):
    universite = models.ForeignKey(Universite, on_delete=models.CASCADE, related_name='ecoles')
    nom = models.CharField(max_length=100)
    nom_detaille = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to='ecoles/logos/', null=True, blank=True)
    description = models.TextField()
    map_iframe = models.TextField(
        blank=True, 
        null=True, 
        help_text="Collez ici le code 'Intégrer une carte' de Google Maps"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Correction update_at -> updated_at

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.universite.nom})"

    def save(self, *args, **kwargs):
        # Logique de logo par défaut héritée de l'université
        if not self.logo and self.universite.logo:
            self.logo = self.universite.logo
        super().save(*args, **kwargs)


class Filiere(models.Model):
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, related_name='filieres')
    nom = models.CharField(max_length=300)
    debouches = models.TextField()
    
    series_autorisees = models.ManyToManyField(Serie, related_name='filieres')
    matieres_principales = models.ManyToManyField(Matiere, related_name='filieres')
    admission = models.ManyToManyField(Admission, related_name='filieres')
    
    bourses = models.TextField(null=True, blank=True, help_text="Détails sur les bourses disponibles")
    aides_universitaires = models.TextField(null=True, blank=True, help_text="Détails sur les aides universitaires disponibles")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Correction update_at -> updated_at

    class Meta:
        verbose_name = "Filière"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.ecole.nom})"

    @property
    def get_logo_url(self):
        # Sécurité pour éviter les erreurs si le logo est manquant
        if self.ecole.logo:
            return self.ecole.logo.url
        return "/static/img/default-logo.png" # Chemin vers un logo par défaut
    
    
    
    
class RegleAdmission(models.Model):
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE, related_name='regles')
    serie = models.ForeignKey('Serie', on_delete=models.CASCADE)
    matieres_poids = models.ManyToManyField('Discipline', help_text="Les matières mères comptant pour cette série dans cette filière")

    class Meta:
        verbose_name = "Règle d'admission"
        unique_together = ('filiere', 'serie') # Une seule config par couple (Filière, Série)

    def __str__(self):
        return f"{self.filiere.nom} - Série {self.serie.nom}"
    
