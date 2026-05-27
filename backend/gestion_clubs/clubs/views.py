# clubs/views.py

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404

from accounts.models import Utilisateur
from .models import Club, RoleClub, Adhesion
from .serializers import (
    ClubLectureSerializer,
    ClubCreationSerializer,
    AdhesionLectureSerializer,
    AjoutMembreSerializer,
    GestionRolesSerializer,
    RoleClubSerializer,
)
from .permissions import (
    EstAdministrateur,
    EstPresidentDuClub,
    EstPresidentOuAdministrateur,
    EstMembreDuClub,
)


# ──────────────────────────────────────────────────────────────────
# VUE : LISTE DES CLUBS PUBLICS
# GET /api/clubs/
# Accessible à tous (visiteurs inclus).
# Retourne uniquement les clubs validés.
# ──────────────────────────────────────────────────────────────────
class ListeClubsView(generics.ListAPIView):
    """
    Retourne la liste de tous les clubs validés.
    Accessible sans authentification (page publique).
    """
    serializer_class   = ClubLectureSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Club.objects.filter(statut=Club.VALIDE)


# ──────────────────────────────────────────────────────────────────
# VUE : CRÉATION D'UN CLUB
# POST /api/clubs/creer/
# Tout utilisateur connecté peut soumettre une demande.
# Le club est créé avec le statut EN_ATTENTE.
# L'admin reçoit une notification (à implémenter plus tard).
# ──────────────────────────────────────────────────────────────────
class CreerClubView(generics.CreateAPIView):
    """
    Permet à un utilisateur connecté de soumettre
    une demande de création de club.
    """
    serializer_class   = ClubCreationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            club = serializer.save()

            return Response({
                "message": (
                    "Demande de création envoyée. "
                    "En attente de validation par l'administrateur."
                ),
                "club": ClubLectureSerializer(club).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────────
# VUE : DÉTAIL D'UN CLUB
# GET /api/clubs/<pk>/
# Accessible à tous pour les clubs validés.
# ──────────────────────────────────────────────────────────────────
class DetailClubView(generics.RetrieveAPIView):
    """
    Retourne les détails d'un club spécifique.
    """
    serializer_class   = ClubLectureSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Club.objects.filter(statut=Club.VALIDE)


# ──────────────────────────────────────────────────────────────────
# VUE : VALIDATION D'UN CLUB
# POST /api/clubs/<pk>/valider/
# Réservée à l'administrateur.
# Change le statut EN_ATTENTE → VALIDE.
# Crée automatiquement les rôles par défaut du club.
# Nomme le créateur comme président.
# ──────────────────────────────────────────────────────────────────
class ValiderClubView(APIView):
    """
    L'administrateur valide un club en attente.
    Actions automatiques après validation :
    1. Statut → VALIDE
    2. Création des 4 rôles par défaut (Président, Secrétaire, etc.)
    3. Le créateur devient automatiquement Président
    4. Son rôle système passe à MEMBRE
    """
    permission_classes = [EstAdministrateur]

    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk, statut=Club.EN_ATTENTE)

        # ── 1. Validation du club ─────────────────────────────────
        club.statut         = Club.VALIDE
        club.date_validation = timezone.now()
        club.valide_par     = request.user
        club.save()

        # ── 2. Création des rôles par défaut ──────────────────────
        # Chaque club validé reçoit automatiquement ses 4 rôles
        permissions_par_role = {
            RoleClub.PRESIDENT: [
                'ajouter_membre',
                'retirer_membre',
                'attribuer_role',
                'publier',
                'gerer_activites',
            ],
            RoleClub.SECRETAIRE: [
                'publier',
                'gerer_activites',
            ],
            RoleClub.TRESORIER: [
                'gerer_finances',
            ],
            RoleClub.MEMBRE: [],
        }

        roles_crees = {}
        for libelle, permissions in permissions_par_role.items():
            role, _ = RoleClub.objects.get_or_create(
                libelle=libelle,
                club=club,
                defaults={'permissions': permissions}
            )
            roles_crees[libelle] = role

        # ── 3. Le créateur devient président ──────────────────────
        adhesion, _ = Adhesion.objects.get_or_create(
            utilisateur=club.createur,
            club=club,
            defaults={'ajoute_par': request.user}
        )

        # On lui attribue le rôle président via notre méthode métier
        adhesion.attribuer_role(roles_crees[RoleClub.PRESIDENT])

        # ── 4. Promotion du créateur en MEMBRE système ────────────
        club.createur.promouvoir_en_membre()

        return Response({
            "message": f"Le club '{club.nom}' a été validé avec succès.",
            "club": ClubLectureSerializer(club).data
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────
# VUE : SUSPENSION / ARCHIVAGE D'UN CLUB
# POST /api/clubs/<pk>/suspendre/
# POST /api/clubs/<pk>/archiver/
# Réservées à l'administrateur.
# ──────────────────────────────────────────────────────────────────
class SuspendreClubView(APIView):
    """Suspend un club validé."""
    permission_classes = [EstAdministrateur]

    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk, statut=Club.VALIDE)
        club.statut = Club.SUSPENDU
        club.save()

        return Response({
            "message": f"Le club '{club.nom}' a été suspendu."
        }, status=status.HTTP_200_OK)


class ArchiverClubView(APIView):
    """Archive un club (action irréversible depuis l'API)."""
    permission_classes = [EstAdministrateur]

    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk)
        club.statut = Club.ARCHIVE
        club.save()

        return Response({
            "message": f"Le club '{club.nom}' a été archivé."
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────
# VUE : LISTE DES MEMBRES D'UN CLUB
# GET /api/clubs/<pk>/membres/
# Accessible aux membres du club et à l'admin.
# ──────────────────────────────────────────────────────────────────
class ListeMembresView(generics.ListAPIView):
    """
    Retourne la liste des membres actifs d'un club.
    Réservée aux membres du club et à l'administrateur.
    """
    serializer_class   = AdhesionLectureSerializer
    permission_classes = [EstPresidentOuAdministrateur | EstMembreDuClub]

    def get_queryset(self):
        club_id = self.kwargs.get('pk')
        return Adhesion.objects.filter(
            club_id=club_id,
            est_actif=True
        ).select_related('utilisateur', 'ajoute_par')


# ──────────────────────────────────────────────────────────────────
# VUE : AJOUT D'UN MEMBRE
# POST /api/clubs/<pk>/membres/ajouter/
# Réservée au président du club.
# ──────────────────────────────────────────────────────────────────
class AjouterMembreView(APIView):
    """
    Le président ajoute un utilisateur à son club.
    Il envoie l'email de l'utilisateur et les rôles à attribuer.
    """
    permission_classes = [EstPresidentDuClub]

    def post(self, request, pk):
        club = get_object_or_404(Club, pk=pk, statut=Club.VALIDE)

        serializer = AjoutMembreSerializer(
            data=request.data,
            context={'club': club, 'request': request}
        )

        if serializer.is_valid():
            # Récupère l'utilisateur par son email
            utilisateur = Utilisateur.objects.get(
                email=serializer.validated_data['email']
            )

            # Vérifie que l'utilisateur n'est pas déjà membre
            if Adhesion.objects.filter(
                utilisateur=utilisateur,
                club=club,
                est_actif=True
            ).exists():
                return Response(
                    {"error": "Cet utilisateur est déjà membre du club."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Création de l'adhésion
            adhesion = Adhesion.objects.create(
                utilisateur=utilisateur,
                club=club,
                ajoute_par=request.user
            )

            # Attribution des rôles si fournis
            roles_ids = serializer.validated_data.get('roles_ids', [])
            if roles_ids:
                roles = RoleClub.objects.filter(id__in=roles_ids, club=club)
                for role in roles:
                    adhesion.attribuer_role(role)

            return Response({
                "message": f"{utilisateur.get_full_name()} a été ajouté au club.",
                "adhesion": AdhesionLectureSerializer(adhesion).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────────
# VUE : RETIRER UN MEMBRE
# DELETE /api/clubs/<pk>/membres/<user_pk>/retirer/
# Réservée au président du club.
# ──────────────────────────────────────────────────────────────────
class RetirerMembreView(APIView):
    """
    Le président retire un membre de son club.
    L'adhésion n'est pas supprimée mais désactivée (est_actif=False)
    pour garder l'historique.
    """
    permission_classes = [EstPresidentDuClub]

    def delete(self, request, pk, user_pk):
        club     = get_object_or_404(Club, pk=pk, statut=Club.VALIDE)
        adhesion = get_object_or_404(
            Adhesion,
            club=club,
            utilisateur_id=user_pk,
            est_actif=True
        )

        # Empêche le président de se retirer lui-même
        if adhesion.utilisateur == request.user:
            return Response(
                {"error": "Vous ne pouvez pas vous retirer vous-même du club."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Désactivation de l'adhésion (soft delete)
        adhesion.est_actif = False
        adhesion.date_fin  = timezone.now().date()
        adhesion.save()

        return Response(
            {"message": f"{adhesion.utilisateur.get_full_name()} a été retiré du club."},
            status=status.HTTP_200_OK
        )


# ──────────────────────────────────────────────────────────────────
# VUE : GESTION DES RÔLES D'UN MEMBRE
# PUT /api/clubs/<pk>/membres/<user_pk>/roles/
# Président : peut modifier les rôles simples
# Administrateur : peut aussi transférer le rôle président
# ──────────────────────────────────────────────────────────────────
class GererRolesMembreView(APIView):
    """
    Modifie les rôles d'un membre dans un club.
    - Le président peut attribuer/retirer les rôles simples.
    - Seul l'administrateur peut transférer le rôle de président.
    """
    permission_classes = [EstPresidentOuAdministrateur]

    def put(self, request, pk, user_pk):
        club     = get_object_or_404(Club, pk=pk, statut=Club.VALIDE)
        adhesion = get_object_or_404(
            Adhesion,
            club=club,
            utilisateur_id=user_pk,
            est_actif=True
        )

        serializer = GestionRolesSerializer(
            data=request.data,
            context={'club': club, 'request': request}
        )

        if serializer.is_valid():
            roles_ids    = serializer.validated_data['roles_ids']
            nouveaux_roles = RoleClub.objects.filter(
                id__in=roles_ids,
                club=club
            )

            # Remplacement complet des rôles via notre méthode métier
            adhesion.remplacer_tous_les_roles(nouveaux_roles)

            return Response({
                "message": "Rôles mis à jour avec succès.",
                "adhesion": AdhesionLectureSerializer(adhesion).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)