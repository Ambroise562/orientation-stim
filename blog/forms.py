from django import forms
from .models import Serie, Discipline

class SimulateurForm(forms.Form):
    # On définit les noms exacts des séries que tu veux autoriser
    SERIES_AUTORISEES = ['Bac A1', 'Bac A2', 'Bac B', 'Bac C', 'Bac D', 'Bac E', 'Bac F1', 'Bac F2', 'Bac F3', 'Bac F4', 'Bac G1', 'Bac G2', 'Bac G3']

    serie = forms.ModelChoiceField(
        queryset=Serie.objects.filter(nom__in=SERIES_AUTORISEES),
        label="Sélectionnez votre Série au BAC",
        empty_label="Choisir une série...",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'serie-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On affiche dynamiquement tous les champs de notes possibles
        disciplines = Discipline.objects.all()
        for d in disciplines:
            self.fields[f'note_{d.id}'] = forms.FloatField(
                label=d.nom,
                required=False,
                min_value=0,
                max_value=20,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control note-input',
                    'step': '0.01',
                    'placeholder': '0'
                })
            )
            
            