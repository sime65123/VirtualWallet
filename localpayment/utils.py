import random
import string

def generate_unique_code(length=5):
    # Créez une liste de caractères possibles (lettres majuscules, minuscules et chiffres)
    characters = string.ascii_letters + string.digits + string.punctuation

    # Générez un code aléatoire de la longueur spécifiée
    unique_code = ''.join(random.choice(characters) for _ in range(length))

    return unique_code

# Exemple d'utilisation
code = generate_unique_code()
print(f"Code généré : {code}")
