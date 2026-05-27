# clubs/urls.py 

from django.urls import path
from .views import (
    ListeClubsView,
    CreerClubView,
    DetailClubView,
    ValiderClubView,
    SuspendreClubView,
    ArchiverClubView,
    ListeMembresView,
    AjouterMembreView,
    RetirerMembreView,
    GererRolesMembreView,
    # ── Publications ──────────────────────────────────────────────
    ListePublicationsView,
    CreerPublicationView,
    PublicationsEnAttenteView,
    ValiderPublicationView,
    PublicationsClubView,
    # ── Statistiques ──────────────────────────────────────────────
    StatistiquesView
)

urlpatterns = [

    # ── Clubs publics ─────────────────────────────────────────────
    path('', ListeClubsView.as_view(), name='liste_clubs'),
    path('<int:pk>/', DetailClubView.as_view(), name='detail_club'),

    # ── Création club ─────────────────────────────────────────────
    path('creer/', CreerClubView.as_view(), name='creer_club'),

    # ── Actions admin sur les clubs ───────────────────────────────
    path('<int:pk>/valider/', ValiderClubView.as_view(), name='valider_club'),
    path('<int:pk>/suspendre/', SuspendreClubView.as_view(), name='suspendre_club'),
    path('<int:pk>/archiver/', ArchiverClubView.as_view(), name='archiver_club'),

    # ── Membres ───────────────────────────────────────────────────
    path('<int:pk>/membres/', ListeMembresView.as_view(), name='liste_membres'),
    path('<int:pk>/membres/ajouter/', AjouterMembreView.as_view(), name='ajouter_membre'),
    path('<int:pk>/membres/<int:user_pk>/retirer/', RetirerMembreView.as_view(), name='retirer_membre'),
    path('<int:pk>/membres/<int:user_pk>/roles/', GererRolesMembreView.as_view(), name='gerer_roles'),

    # ── Publications par club ─────────────────────────────────────
    path('<int:pk>/publications/', PublicationsClubView.as_view(), name='publications_club'),
    path('<int:pk>/publications/creer/', CreerPublicationView.as_view(), name='creer_publication'),

    # ── Publications globales ─────────────────────────────────────
    path('publications/', ListePublicationsView.as_view(), name='liste_publications'),
    path('publications/en-attente/', PublicationsEnAttenteView.as_view(), name='publications_en_attente'),
    path('publications/<int:pub_pk>/valider/', ValiderPublicationView.as_view(), name='valider_publication'),
    
    # ── Statistiques globales ─────────────────────────────────────
    path('statistiques/', StatistiquesView.as_view(), name='statistiques'),
]