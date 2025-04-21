from django.contrib import admin
from .models import Utilisateur, Lavage, Compte, Transaction,Ville

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display=['nom']
# Enregistrement du modèle Utilisateur
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['email', 'pseudo', 'numero_telephone', 'ville_residence', 'is_active', 'is_admin']
    search_fields = ['email', 'pseudo']
    list_filter = ['is_active', 'is_admin']
    ordering = ['email']

# Enregistrement du modèle Lavage
@admin.register(Lavage)
class LavageAdmin(admin.ModelAdmin):
    list_display = ['codeQR', 'date', 'utilisateur', 'statut']
    search_fields = ['codeQR', 'utilisateur__pseudo']
    list_filter = ['statut']
    ordering = ['date']

# Enregistrement du modèle Compte
@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ['numero_compte', 'solde', 'utilisateur']
    search_fields = ['numero_compte', 'utilisateur__pseudo']
    ordering = ['numero_compte']

# Enregistrement du modèle Transaction
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'montant', 'date_transaction', 'utilisateur', 'numero_emetteur', 'statut']
    search_fields = ['transaction_id', 'utilisateur__pseudo']
    list_filter = ['statut']
    ordering = ['date_transaction']
