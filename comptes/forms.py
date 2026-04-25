from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profil

# 1. Formulaire d'INSCRIPTION (Utilisé une seule fois à la création)
class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

# 2. Formulaire de MODIFICATION des identifiants (Username/Email)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill'}),
        }

# 3. Formulaire de MODIFICATION du Profil (Série, Bio, etc.)
class ProfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['type_utilisateur', 'serie', 'etablissement', 'bio', 'photo']
        widgets = {
            'type_utilisateur': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'serie': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'etablissement': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Ex: UAC / ENEAM'}),
            'bio': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
        }