# accounts/views.py

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Utilisateur
from .serializers import (
    InscriptionSerializer,
    UtilisateurProfilSerializer,
    ChangerMotDePasseSerializer
)


# ──────────────────────────────────────────────────────────────────
# VUE D'INSCRIPTION
# POST /api/auth/register/
# Accessible à tous (AllowAny) — pas besoin d'être connecté
# ──────────────────────────────────────────────────────────────────
class InscriptionView(generics.CreateAPIView):
    """
    Permet à un visiteur de créer un compte.
    Le rôle attribué par défaut est VISITEUR.
    """
    queryset = Utilisateur.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [AllowAny]  # ← Pas besoin d'être connecté

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            utilisateur = serializer.save()

            # On génère un token JWT immédiatement après l'inscription
            # pour que l'utilisateur n'ait pas à se reconnecter
            refresh = RefreshToken.for_user(utilisateur)

            return Response({
                "message": "Compte créé avec succès.",
                "utilisateur": UtilisateurProfilSerializer(utilisateur).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────────
# VUE DE DÉCONNEXION
# POST /api/auth/logout/
# Blackliste le refresh token pour invalider la session
# ──────────────────────────────────────────────────────────────────
class DeconnexionView(APIView):
    """
    Déconnecte l'utilisateur en blacklistant son refresh token.
    Après ça, le token ne pourra plus être utilisé pour
    obtenir un nouvel access token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Le refresh token est requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # On blackliste le token → il ne fonctionnera plus
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Déconnexion réussie."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ──────────────────────────────────────────────────────────────────
# VUE PROFIL UTILISATEUR
# GET  /api/auth/me/  → lire son profil
# PUT  /api/auth/me/  → modifier nom, prénom, photo
# ──────────────────────────────────────────────────────────────────
class ProfilView(generics.RetrieveUpdateAPIView):
    """
    Permet à un utilisateur connecté de voir et modifier son profil.
    request.user contient automatiquement l'utilisateur
    identifié par le token JWT.
    """
    serializer_class = UtilisateurProfilSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # On retourne uniquement l'utilisateur connecté
        # Impossible de voir le profil de quelqu'un d'autre
        return self.request.user


# ──────────────────────────────────────────────────────────────────
# VUE CHANGEMENT DE MOT DE PASSE
# POST /api/auth/changer-password/
# ──────────────────────────────────────────────────────────────────
class ChangerMotDePasseView(APIView):
    """
    Permet à un utilisateur connecté de changer son mot de passe.
    On vérifie d'abord l'ancien mot de passe avant d'appliquer le nouveau.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data)

        if serializer.is_valid():
            utilisateur = request.user

            # Vérification de l'ancien mot de passe
            if not utilisateur.check_password(
                serializer.validated_data['ancien_password']
            ):
                return Response(
                    {"ancien_password": "Mot de passe actuel incorrect."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Application du nouveau mot de passe (hashé automatiquement)
            utilisateur.set_password(
                serializer.validated_data['nouveau_password']
            )
            utilisateur.save()

            return Response(
                {"message": "Mot de passe modifié avec succès."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)