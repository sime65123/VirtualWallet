import qrcode
from cryptography.fernet import Fernet
import random
from datetime import datetime
import hashlib
import base64
import base64
from io import BytesIO

# ... vos autres fonctions ...

def generer_qr_code_base64(data_chiffree):
    img = generer_qr_code(data_chiffree)  # Utilisez la fonction existante pour créer l'image
    buffer = BytesIO()
    img.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()

def generer_qr_code(data_chiffree):
    # Créer un objet QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Ajouter les données chiffrées au QR Code
    qr.add_data(data_chiffree)
    qr.make(fit=True)

    # Créer une image du QR Code et la sauvegarder
    img = qr.make_image(fill='black', back_color='white')
    nom_fichier = datetime.now().strftime("%Y%m%d-%H%M%S") + '_qr.png'
    chemin_complet = 'static/qrcode/' + nom_fichier
    img.save(chemin_complet)
    return chemin_complet
def generer_code_unique2():
    # Obtenir la date et l'heure actuelles
    maintenant = datetime.now()
    # Convertir en chaîne de caractères avec un format spécifique
    date_str = maintenant.strftime("%Y%m%d%H%M%S%f")
    # Générer un nombre aléatoire
    random_number = random.SystemRandom().randint(100000, 999999)
    # Concaténer la date, le nombre aléatoire et un sel
    sel = hashlib.sha256(random_number.to_bytes(3, 'big')).hexdigest()
    code_unique = f"{date_str}{sel}"
    # Utiliser SHA-256 pour hasher le code
    hash_code_unique = hashlib.sha256(code_unique.encode()).hexdigest()
    return hash_code_unique
# Générer une clé de chiffrement
def generer_cle_chiffrement():
    return Fernet.generate_key()

# Chiffrer les données
def chiffrer_donnees(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

# Déchiffrer les données
def dechiffrer_donnees(data_chiffree, key):
    fernet = Fernet(key)
    return fernet.decrypt(data_chiffree).decode()




def encoder_image_base64(chemin_image):
    # Ouvrir l'image
    with open(chemin_image, "rb") as image_file:
        # Encoder l'image en base64
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('utf-8')

# Utilisation de la fonction
# chemin_image = 'chemin/vers/votre/image.png'  # Remplacez par le chemin réel de votre image
# image_base64 = encoder_image_base64(chemin_image)
# print(image_base64)



# # Exemple d'utilisation
# cle = generer_cle_chiffrement()
# print("Clé de chiffrement:", cle)
# # Exemple d'utilisation
# code = generer_code_unique2()
# print("Le code unique généré 2 est :", code)

# code_chiffre = chiffrer_donnees(code, cle)
# print("Code chiffré:", code_chiffre)

# code_dechiffre = dechiffrer_donnees(code_chiffre, cle)
# print("Code déchiffré:", code_dechiffre)

# # Exemple d'utilisation
# # Supposons que 'code_chiffre' est votre code chiffré obtenu précédemment
# img_qr = generer_qr_code(code_chiffre)
# #img_qr.show()  # Afficher l'image du QR Code
