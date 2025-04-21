from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription3, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('activation/<uidb64>/<token>/', views.activation, name='activation'),
    path('confirmation/', views.page_de_confirmation, name='page_de_confirmation'),
    path('chargement/', views.initier_transaction, name='page_de_chargement_compte'),
    path('chargement2/', views.initier_transaction2, name='page_de_chargement_compte2'),
    path('', views.home, name='home'),
    path('vitrine', views.vitrine, name='vitrine'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('create-account/<str:email>/', views.create_view, name='create-account'),
    path('profil', views.profil, name='profil'),
    path(' update_password', views.changer_mot_de_passe, name='update_password'),

   


   

    # Ajoutez d'autres chemins pour vos vues ici
]
