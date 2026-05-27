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
)

urlpatterns = [

    # ── Clubs publics ─────────────────────────────────────────────
    path('', ListeClubsView.as_view(), name='liste_clubs'),
    path('<int:pk>/', DetailClubView.as_view(), name='detail_club'),

    # ── Création ──────────────────────────────────────────────────
    path('creer/', CreerClubView.as_view(), name='creer_club'),

    # ── Actions administrateur ────────────────────────────────────
    path('<int:pk>/valider/', ValiderClubView.as_view(), name='valider_club'),
    path('<int:pk>/suspendre/', SuspendreClubView.as_view(), name='suspendre_club'),
    path('<int:pk>/archiver/', ArchiverClubView.as_view(), name='archiver_club'),

    # ── Gestion des membres (président) ──────────────────────────
    path('<int:pk>/membres/', ListeMembresView.as_view(), name='liste_membres'),
    path('<int:pk>/membres/ajouter/', AjouterMembreView.as_view(), name='ajouter_membre'),
    path('<int:pk>/membres/<int:user_pk>/retirer/', RetirerMembreView.as_view(), name='retirer_membre'),
    path('<int:pk>/membres/<int:user_pk>/roles/', GererRolesMembreView.as_view(), name='gerer_roles'),
]