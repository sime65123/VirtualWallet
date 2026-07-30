from django.shortcuts import render
from datetime import datetime
from django.utils.http import urlsafe_base64_decode
from datetime import datetime
from django.shortcuts import render, redirect
from .forms import InscriptionForm
from .models import Utilisateur, Lavage
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
            # Enregistrer le lavage en base de données
            Lavage.objects.create(
                codeQR=code_chiffre,
                utilisateur=compte.utilisateur
            )
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
    from django.utils import timezone
    import datetime as dt
    user = request.user
    try:
        compte = Compte.objects.get(utilisateur=user)
        solde = compte.solde
    except Compte.DoesNotExist:
        compte = Compte.objects.create(utilisateur=user, solde=0)
        solde = 0

    today = timezone.now().date()
    max_date = today + dt.timedelta(days=30)

    return render(request, 'profil.html', {
        'solde':    solde,
        'today':    today.strftime('%Y-%m-%d'),
        'max_date': max_date.strftime('%Y-%m-%d'),
    })


from django.shortcuts import render, redirect
from .models import Transaction, Utilisateur, Compte
from .forms import TransactionForm
from django.contrib import messages
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json as json_module

def initier_transaction(request):
    if request.method == 'POST':
        numero_emetteur = request.POST.get('numero_emetteur', '').strip()
        montant_str     = request.POST.get('montant', '0').strip()

        try:
            montant = int(float(montant_str))
        except ValueError:
            messages.error(request, "Montant invalide.")
            return redirect('profil')

        montant = (montant // 5) * 5
        if montant < 100:
            messages.error(request, "Le montant minimum est de 100 XAF.")
            return redirect('profil')

        timestamp      = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_number  = str(random.randint(0, 999999))
        transaction_id = timestamp + random_number

        # On enregistre la transaction en attente
        transaction = Transaction.objects.create(
            utilisateur     = request.user,
            montant         = montant,
            numero_emetteur = numero_emetteur,
            transaction_id  = transaction_id,
            statut          = 'En attente'
        )

        # On redirige vers la page de paiement avec les paramètres
        request.session['pending_transaction_id'] = transaction_id
        request.session['pending_montant']        = montant
        request.session['pending_numero']         = numero_emetteur
        return redirect('page_paiement_cinetpay')

    return redirect('vitrine')




def page_paiement_cinetpay(request):
    transaction_id = request.session.get('pending_transaction_id')
    montant        = request.session.get('pending_montant')
    numero         = request.session.get('pending_numero')

    if not transaction_id:
        messages.error(request, "Session expirée. Veuillez recommencer.")
        return redirect('profil')

    notify_url = 'https://nebulizer-vagrancy-ragweed.ngrok-free.dev/emailApp/transaction/notification/'
    return_url = 'https://nebulizer-vagrancy-ragweed.ngrok-free.dev/emailApp/transaction/retour/'

    context = {
        'transaction_id': transaction_id,
        'montant':        montant,
        'numero':         numero,
        'notify_url':     notify_url,
        'return_url':     return_url,
        'apikey':         '161273709566393b12aa9b90.88553027',
        'site_id':        '5871717',
        'user_email':     request.user.email,
        'user_name':      request.user.pseudo,
        'user_phone':     '+237' + (numero or ''),
        'user_city':      request.user.ville_residence,
    }
    return render(request, 'paiement_cinetpay.html', context)




import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def cinetpay_notification(request):
    """Webhook appelé par CinetPay après confirmation du paiement."""
    if request.method != 'POST':
        return HttpResponse('Méthode non autorisée.', status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST.dict()

    # Le SDK Seamless envoie cpm_trans_id
    transaction_id = (
        data.get('cpm_trans_id') or
        data.get('transaction_id') or
        data.get('transactionId') or
        ''
    )

    if not transaction_id:
        return HttpResponse('transaction_id manquant.', status=400)

    # Vérifier le statut auprès de CinetPay
    try:
        check = requests.post(
            'https://api-checkout.cinetpay.com/v2/payment/check',
            json={
                'apikey':         '161273709566393b12aa9b90.88553027',
                'site_id':        '5871717',
                'transaction_id': transaction_id,
            },
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        check_data = check.json()
    except Exception as e:
        return HttpResponse(f'Erreur vérification : {e}', status=500)

    if check_data.get('code') == '00':
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            if transaction.statut != 'Succès':
                transaction.statut = 'Succès'
                transaction.save()
                compte = Compte.objects.get(utilisateur=transaction.utilisateur)
                compte.crediter(transaction.montant)
        except Transaction.DoesNotExist:
            pass
        return HttpResponse('OK', status=200)
    else:
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
            transaction.statut = 'Échec'
            transaction.save()
        except Transaction.DoesNotExist:
            pass
        return HttpResponse('Paiement non confirmé.', status=200)


@csrf_exempt
def transaction_retour(request):
    """Page de retour après paiement CinetPay."""
    messages.success(
        request,
        "Votre paiement est en cours de traitement. Votre solde sera mis à jour dans quelques instants."
    )
    return redirect('profil')












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


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def profil_solde_json(request):
    try:
        compte = Compte.objects.get(utilisateur=request.user)
        return JsonResponse({'solde': float(compte.solde)})
    except Compte.DoesNotExist:
        return JsonResponse({'solde': 0})



import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ReservationHoraire, Lavage
from django.contrib.auth.decorators import login_required

@login_required
def creneaux_disponibles(request):
    """Retourne les créneaux déjà réservés pour une date donnée."""
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'erreur': 'Date manquante'}, status=400)
    
    reserves = ReservationHoraire.objects.filter(
        date_passage=date
    ).values_list('heure_passage', flat=True)
    
    # Convertir en liste de strings "HH:MM"
    reserves_list = [h.strftime('%H:%M') for h in reserves]
    return JsonResponse({'reserves': reserves_list})


@csrf_exempt
@require_http_methods(["POST"])
def reserver_horaire(request):
    if not request.user.is_authenticated:
        return JsonResponse({'erreur': 'Non connecté.'}, status=401)
    try:
        data          = json.loads(request.body)
        date_passage  = data.get('date_passage')
        heure_passage = data.get('heure_passage')

        if not date_passage or not heure_passage:
            return JsonResponse({'erreur': 'Date ou heure manquante.'}, status=400)

        # Vérifier que le créneau (date + heure) est libre
        if ReservationHoraire.objects.filter(
            date_passage=date_passage,
            heure_passage=heure_passage
        ).exists():
            return JsonResponse(
                {'erreur': 'Ce créneau est déjà réservé. Choisissez un autre horaire.'},
                status=409
            )

        # Prendre le dernier lavage souscrit par cet utilisateur
        try:
            lavage = Lavage.objects.filter(
                utilisateur=request.user
            ).latest('date')
        except Lavage.DoesNotExist:
            return JsonResponse(
                {'erreur': "Aucun lavage trouvé. Souscrivez d'abord à un lavage."},
                status=404
            )

        # Vérifier que ce lavage n'a pas déjà une réservation
        if ReservationHoraire.objects.filter(lavage=lavage).exists():
            return JsonResponse(
                {'erreur': 'Votre dernier lavage a déjà un créneau programmé.'},
                status=409
            )

        reservation = ReservationHoraire.objects.create(
            utilisateur=request.user,
            lavage=lavage,
            date_passage=date_passage,
            heure_passage=heure_passage
        )

        return JsonResponse({
            'succes': True,
            'message': f'Créneau réservé le {date_passage} à {heure_passage}.'
        })

    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=500)


@login_required
def mes_reservations(request):
    """Retourne les réservations de l'utilisateur connecté."""
    reservations = ReservationHoraire.objects.filter(
        utilisateur=request.user
    ).select_related('lavage').order_by('date_passage', 'heure_passage')
    
    data = [{
        'id':           r.id,
        'date_passage': r.date_passage.strftime('%d/%m/%Y'),
        'heure_passage': r.heure_passage.strftime('%H:%M'),
        'lavage_code':  r.lavage.codeQR,
    } for r in reservations]
    
    return JsonResponse({'reservations': data})