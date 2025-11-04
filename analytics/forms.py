# Em analytics/forms.py
from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [] # <-- A LISTA AGORA ESTÁ VAZIA