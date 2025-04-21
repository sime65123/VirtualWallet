from django.shortcuts import render
from datetime import datetime
from django.utils.http import urlsafe_base64_decode
from datetime import datetime
from django.shortcuts import render, redirect
from .forms import InscriptionForm
from .models import Utilisateur
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
import random
from .utils import send_email_with_html_body,send_email_with_html_body2, send_email_with_html_body3
from .qrgenerator import chiffrer_donnees,generer_code_unique2,generer_qr_code_base64,generer_cle_chiffrement,generer_qr_code,encoder_image_base64
from django.core.mail import EmailMessage
import logging
from django.conf import settings

# Create your views here.
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404
from .models import Compte, Utilisateur

def recuperer_solde(request, email_client):
    # Récupérer l'utilisateur par email
    utilisateur = get_object_or_404(Utilisateur, email=email_client)
    
    # Récupérer le compte associé à l'utilisateur
    compte = get_object_or_404(Compte, utilisateur=utilisateur)
    
    # Récupérer le solde du compte
    solde = compte.solde
    
    # Vous pouvez maintenant retourner le solde ou l'utiliser comme vous le souhaitez
    return solde,compte


def create_view(request, email):
    """This view help to create and account for testing sending mails"""
    solde,compte=recuperer_solde(request, email)
    if(solde>=5000):
        compte.debiter(5000)
        cxt = {}
        subjet = 'Souscription de Lavage reussi'
        template = 'email.html'
        cle = generer_cle_chiffrement()
        code = generer_code_unique2()
        code_chiffre = chiffrer_donnees(code, cle)
        chemin_qr_code_image = generer_qr_code(code_chiffre)
        encode_base64 = encoder_image_base64(chemin_qr_code_image)


        context = {
            'date': datetime.today().date(),
            'email': email,
            'chemin_qr_code_image': chemin_qr_code_image,
            'image_base64': encode_base64
        }

        receivers = [email]

        has_send = send_email_with_html_body2(
            subject=subjet,
            receivers=receivers,
            template=template,
            context=context,
            attachment_path=chemin_qr_code_image
        )

        if has_send:
            
            cxt = {"msg": "mail envoyee avec success"}
            return render(request, 'email.html', context)
        else:
            cxt = {"msg": "erreur lors de l'envoi du mail"}
            return render(request, 'email.html', cxt)
    else:
        cxt = {}
        subjet = 'Souscription de Lavage échoué'
        template = 'emailE.html'
       

        context = {
            'date': datetime.today().date(),
            'email': email,
        
        }

        receivers = [email]

        has_send = send_email_with_html_body3(
            subject=subjet,
            receivers=receivers,
            template=template,
            context=context,
         
        )

        if has_send:
            cxt = {"msg": "mail envoyee avec success"}
            return render(request, 'emailE.html', context)
        else:
            cxt = {"msg": "erreur lors de l'envoi du mail"}
            return render(request, 'emailE.html', cxt)


    








def activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # Connectez l'utilisateur ici si vous le souhaitez
        return redirect('home')  # Redirigez vers la page d'accueil
    else:
        return render(request, 'activation_invalid.html')  # Affichez une erreur si le lien n'est pas valide
    

def page_de_confirmation(request):
    # Vous pouvez ajouter de la logique supplémentaire ici si nécessaire
    return render(request, 'page_de_confirmation.html')



def home(request):
    # Vous pouvez ajouter de la logique supplémentaire ici si nécessaire
    return render(request, 'vitrine.html')


#zjrf irmp wkdk ydrb
def profil(request):
    user=request.user
    solde=Compte.objects.get(utilisateur=user).solde
    context={
        'solde':solde
    }
    # Vous pouvez ajouter de la logique supplémentaire ici si nécessaire
    return render(request, 'profil.html',context)


from django.shortcuts import render, redirect
from .models import Transaction, Utilisateur, Compte
from .forms import TransactionForm
from django.contrib import messages
import requests

def initier_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.utilisateur = request.user

              # Obtenir le temps actuel en microsecondes
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')

            # Générer un nombre aléatoire et le convertir en chaîne de caractères
            random_number = str(random.randint(0, 999999))

            # Concaténer le timestamp et le nombre aléatoire pour obtenir un identifiant unique
            unique_number = timestamp + random_number

            transaction.transaction_id=unique_number
            #transaction.save()
                # Appel API Cinetpay pour initier le paiement
            response = requests.post('https://api-checkout.cinetpay.com/v2/payment', data={
                'apikey': '161273709566393b12aa9b90.88553027',
                'site_id': '5871717',
                'transaction_id': transaction.transaction_id,
                'currency': 'XAF',
                'description': 'Dépôt sur compte',
                'amount': transaction.montant,      
                'channels': 'ALL',
                #Fournir ces variables pour le paiements par carte bancaire
                'customer_name': transaction.utilisateur.pseudo ,      
                'customer_email': transaction.utilisateur.email,
                'customer_phone_number': '+237'+transaction.numero_emetteur,
                'customer_address' : "",
                'customer_city': transaction.utilisateur.ville_residence,
                'customer_country' : "CM",
                'customer_state' : "CM",
                'customer_zip_code' : "", 
                'return_url': request.build_absolute_uri('/transaction/retour/'),
                'notify_url': request.build_absolute_uri('/transaction/notification/')
            })
            print("-------------------------------------------------------"+str(response.json()))#659070872




    #         response2 = requests.post('https://api-checkout.cinetpay.com/v2/payment/check', json={
    #         'apikey': '161273709566393b12aa9b90.88553027',
    #         'site_id': '5871717',
    #         'transaction_id': transaction.transaction_id,
    #     })

    #     if response2.status_code == 200:
    #         transaction_data = response2.json()
    #         if transaction_data['code'] == '00':  # Vérifiez si la transaction est réussie
    #             # Mettez à jour le statut de la transaction dans votre base de données
    #             # ...
    #             return HttpResponse('Transaction réussie et confirmée.')
    #         else:
    #             return HttpResponse('Échec de la transaction.', status=400)
    #     else:
    #         return HttpResponse('Erreur lors de la vérification de la transaction.', status=500)
    # return HttpResponse('Méthode non autorisée.', status=405)

            if response.status_code == 200:
                # Rediriger l'utilisateur vers la page de paiement Cinetpay
                subject = "Activation reussi"
                receivers = [transaction.utilisateur.email]
                template = "email.html"  # Assurez-vous que ce template existe dans votre dossier de templates
                context = {
                    'variable1': 'valeur1',
                    'variable2': 'valeur2',
                    # ... autres variables de contexte ...
                }
                return redirect(response.json()['data']['payment_url'])
            

            else:
                messages.error(request, "Erreur lors de l'initiation du paiement.")
    else:
        form = TransactionForm()
    return redirect('vitrine')




import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def cinetpay_notification(request):
    if request.method == 'POST':
        # Parsez le JSON reçu de CinetPay
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')

        # Vérifiez le statut de la transaction avec l'API de CinetPay
        response = requests.post('https://api-checkout.cinetpay.com/v2/payment/check', json={
            'apikey': 'votre_apikey',
            'site_id': 'votre_site_id',
            'transaction_id': transaction_id,
        })

        if response.status_code == 200:
            transaction_data = response.json()
            if transaction_data['code'] == '00':  # Vérifiez si la transaction est réussie
                # Mettez à jour le statut de la transaction dans votre base de données
                # ...
                return HttpResponse('Transaction réussie et confirmée.')
            else:
                return HttpResponse('Échec de la transaction.', status=400)
        else:
            return HttpResponse('Erreur lors de la vérification de la transaction.', status=500)
    return HttpResponse('Méthode non autorisée.', status=405)












from django.shortcuts import redirect
from django.contrib import messages
from .forms import TransactionForm
from datetime import datetime
import random
import requests

def initier_transaction2(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.utilisateur = request.user
            transaction.numero_emetteur = form.cleaned_data['numero_emetteur']

            # Générer un identifiant unique pour la transaction
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            random_number = str(random.randint(0, 999999))
            unique_number = timestamp + random_number
            transaction.transaction_id = unique_number

            # Appel API Cinetpay pour initier le paiement
            response = requests.post('https://api-checkout.cinetpay.com/v2/payment', data={
                # ... vos données ...
            })

            if response.status_code == 200:
                response_data = response.json()
                if response_data['code'] == '201':  # Vérifiez le code de statut retourné par CinetPay
                    # Vérifier l'état de la transaction
                    check_response = requests.post('https://api-checkout.cinetpay.com/v2/payment/check', data={
                        'apikey': '161273709566393b12aa9b90.88553027',
                        'site_id': '5871717',
                        'transaction_id': transaction.transaction_id,
                    })
                    check_data = check_response.json()
                    if check_data['code'] == '00':  # Vérifiez si la transaction est réussie
                        transaction.save()  # Ajouter la transaction à la base de données
                        return redirect(response_data['data']['payment_url'])
                    else:
                        messages.error(request, "La transaction a échoué.")
                else:
                    messages.error(request, "Erreur lors de l'initiation du paiement.")
            else:
                messages.error(request, "Erreur lors de la connexion à Cinetpay.")
        else:
            messages.error(request, "Données de formulaire invalides.")
    else:
        return redirect('vitrine')


















from .models import Ville

# def inscription3(request):
#     message="toto"
#     villes=Ville.objects.all()
#     context={
#         'message':message,
#         'villes':villes,
#     }
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         pseudo = request.POST.get('pseudo')
#         numero_telephone = request.POST.get('numero_telephone')
#         ville_residence = request.POST.get('ville_residence')
#         password1 = request.POST.get('password1')
#         form = InscriptionForm(request.POST)
#         user = form.save(commit=False)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#             current_site = get_current_site(request)
#             subject = 'Activez votre compte'

#             context = {
#                 'user': user,
#                 'domain': current_site.domain,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'token': account_activation_token.make_token(user),
#             }
#             html_content = render_to_string('acc_active_email.html', context)
#             email = EmailMultiAlternatives(subject, None, to=[user.email])
#             email.attach_alternative(html_content, "text/html")
#             email.send()
#             message="erreur lors de l'enregistrement "
#             context={
#         'message':message,
#         'villes':villes,
#     }
#             return redirect('page_de_confirmation')
#         else:
#             return render(request, 'log.html',context)
#     else:
#         return render(request, 'log.html',context)




from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .forms import InscriptionForm
from .models import Utilisateur, Compte

def inscription3(request):
    message = "toto"
    villes = Ville.objects.all()
    context = {
        'message': message,
        'villes': villes,
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        pseudo = request.POST.get('pseudo')
        numero_telephone = request.POST.get('numero_telephone')
        ville_residence = request.POST.get('ville_residence')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(f"{email}-----------------{pseudo}-----------------{numero_telephone}-------------------------{ville_residence}------------------{password1}-------------------{password2}")
        form = InscriptionForm(request.POST)
    
        if form.is_valid():
            print("------------------------------------------------------------------------2")
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Créer un compte avec un solde de 0 pour le nouvel utilisateur
            Compte.objects.create(utilisateur=user, solde=0)
            
            current_site = get_current_site(request)
            subject = 'Activez votre compte'
            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            html_content = render_to_string('acc_active_email.html', context)
            email = EmailMultiAlternatives(subject, None, to=[user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return redirect('page_de_confirmation')
        else:
            print("------------------------------------------------------------------------3")
            message = "erreur lors de l'enregistrement"
            context = {
                'message': message,
                'villes': villes,
            }
            return render(request, 'log.html', context)
    else:
        print("------------------------------------------------------------------------4")
        return render(request, 'log.html', context)



    



def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            print("---------------------------------------------------------------------------1")
            return redirect('vitrine')
        else:
            # Retourner un message d'erreur si la connexion échoue
            return render(request, 'log.html', {'error': 'Email ou mot de passe incorrect.'})
    return render(request, 'log.html')


def vitrine(request):
    
    return render(request,'vitrine.html')

def logout_view(request):
    logout(request)  # Utilisez logout pour déconnecter l'utilisateur
    return redirect('vitrine')





from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def changer_mot_de_passe(request):
        ancien_mot_de_passe = request.POST.get('ancien_mot_de_passe')
        nouveau_mot_de_passe = request.POST.get('nouveau_mot_de_passe')
        confirmation_mot_de_passe = request.POST.get('confirmation_mot_de_passe')
        print(f"--------------------------{nouveau_mot_de_passe}----------------------------------{confirmation_mot_de_passe}")

        if request.user.check_password(ancien_mot_de_passe):
            if nouveau_mot_de_passe == confirmation_mot_de_passe:
                request.user.set_password(nouveau_mot_de_passe)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Met à jour la session d'authentification
                print("-------------------------------------------------ok1")
                messages.success(request, "Votre mot de passe a été modifié avec succès.")
                return redirect('profil')  # Redirige vers la page de profil ou une autre vue
            else:
                messages.error(request, "Le nouveau mot de passe et la confirmation ne correspondent pas.")
                print("-------------------------------------------------ok2")
                return redirect('profil')
        else:
            messages.error(request, "L'ancien mot de passe est incorrect.")
            print("-------------------------------------------------ok3")
            return redirect('profil')


