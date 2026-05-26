# accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # Login → retourne access + refresh token
    TokenRefreshView,      # Rafraîchit l'access token avec le refresh token
)
from .views import (
    InscriptionView,
    DeconnexionView,
    ProfilView,
    ChangerMotDePasseView,
)

urlpatterns = [
    # ── Inscription ──────────────────────────────────────────────
    # Crée un nouveau compte
    path('register/', InscriptionView.as_view(), name='inscription'),

    # ── Connexion ────────────────────────────────────────────────
    # Fourni par simplejwt : envoie email+password, reçoit les tokens
    path('login/', TokenObtainPairView.as_view(), name='connexion'),

    # ── Refresh token ────────────────────────────────────────────
    # Obtenir un nouvel access token sans se reconnecter
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ── Déconnexion ──────────────────────────────────────────────
    path('logout/', DeconnexionView.as_view(), name='deconnexion'),

    # ── Profil ───────────────────────────────────────────────────
    # GET → voir son profil / PUT → modifier son profil
    path('me/', ProfilView.as_view(), name='profil'),

    # ── Mot de passe ─────────────────────────────────────────────
    path('changer-password/', ChangerMotDePasseView.as_view(), name='changer_password'),
]