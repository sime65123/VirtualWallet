from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.conf import settings
import logging
from django.conf import settings
from django.core.mail import EmailMessage
# from django_cryptography.fields import encrypt

# from fernet_fields import EncryptedTextField


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Cette méthode est appelée pour générer la valeur de hachage qui sera utilisée dans le token
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )



# Création d'un gestionnaire personnalisé pour notre modèle utilisateur personnalisé
class UtilisateurManager(BaseUserManager):
    def create_user(self, email, pseudo, numero_telephone, ville_residence, password=None):
        if not email:
            raise ValueError('Les utilisateurs doivent avoir une adresse email')
        if not pseudo:
            raise ValueError('Les utilisateurs doivent avoir un pseudo')

        user = self.model(
            email=self.normalize_email(email),
            pseudo=pseudo,
            numero_telephone=numero_telephone,
            ville_residence=ville_residence,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pseudo, numero_telephone, ville_residence, password):
        user = self.create_user(
            email,
            password=password,
            pseudo=pseudo,
            numero_telephone=numero_telephone,
            ville_residence=ville_residence,
        )
        user.is_admin = True
        user.is_active = True  # Assurez-vous que l'utilisateur est actif
        user.save(using=self._db)

        return user
account_activation_token = ActivationTokenGenerator()
# Modèle pour l'utilisateur
class Utilisateur(AbstractBaseUser):
    email = models.EmailField(verbose_name='adresse email', max_length=255, unique=True)
    pseudo = models.CharField(max_length=50, unique=True)
    numero_telephone = models.CharField(max_length=15, unique=True)
    ville_residence = models.CharField(max_length=100)
    #is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  # Le compte n'est pas actif par défaut
    account_activation_token = account_activation_token
    objects = UtilisateurManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pseudo', 'numero_telephone', 'ville_residence']
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

   

    def get_email(self):
        return self.email

    def s_authentifier(self):
        # Logique d'authentification
        pass

# Modèle pour le lavage
class Lavage(models.Model):
    codeQR = models.CharField(max_length=255, unique=True, primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    statut = models.BooleanField(default=True)

    def valider(self):
        # Logique de validation du lavage
        self.statut = False
        self.save()

# Modèle pour le compte
import uuid
from django.db import models

class Compte(models.Model):
    numero_compte = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)

    def debiter(self, montant:int):
        if montant > 0 and self.solde >= montant:
            self.solde -= montant
            self.save()
        else:
            # Gérer l'erreur si le montant est négatif ou si le solde est insuffisant
            pass

    def crediter(self, montant):
        if montant > 0:
            self.solde += montant
            self.save()
        else:
            # Gérer l'erreur si le montant est négatif
            pass




class Transaction(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, unique=True)
    numero_emetteur = models.CharField(max_length=20)
    statut = models.CharField(max_length=20, default='En attente')

    def __str__(self):
        return f"Transaction {self.transaction_id} par {self.utilisateur.pseudo}"


class Ville(models.Model):
    nom=models.CharField(max_length=50)