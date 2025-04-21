from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Transaction

class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True)
    pseudo = forms.CharField(required=True)
    numero_telephone = forms.CharField(required=True)
    ville_residence = forms.CharField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('pseudo', 'email', 'numero_telephone', 'ville_residence', 'password1', 'password2')


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['montant', 'numero_emetteur']  # Ajoutez le champ 'numero_emetteur'
