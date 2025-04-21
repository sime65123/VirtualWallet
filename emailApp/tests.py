from django.test import TestCase, Client
from .views import initier_transaction
from .models import Utilisateur

class MyTestCase(TestCase):
    def setUp(self):
        # Création d'un utilisateur pour le test avec un mot de passe haché
        self.user = Utilisateur.objects.create_user(email='discovery@gmail.com', pseudo='tchak', numero_telephone="68888888", ville_residence="Douala")
        self.user.set_password('tchakounte')
        self.user.save()
        self.client = Client()

    def test_view_with_authenticated_user(self):
        # Connexion de l'utilisateur
        login = self.client.login(email='tchambaedwin@gmail.com', password='tchakounte')
        self.assertTrue(login)

        # Appel de la vue avec l'utilisateur authentifié
        response = self.client.get('page_de_chargement_compte')
        self.assertEqual(response.status_code, 200)
        # Autres assertions et tests
