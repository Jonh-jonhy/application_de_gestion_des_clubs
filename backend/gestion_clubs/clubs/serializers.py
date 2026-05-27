# clubs/serializers.py

from rest_framework import serializers
from django.utils import timezone
from .models import Club, RoleClub, Adhesion
from accounts.serializers import UtilisateurProfilSerializer


# ──────────────────────────────────────────────────────────────────
# SERIALIZER RÔLE CLUB
# Utilisé pour afficher et créer les rôles d'un club.
# ──────────────────────────────────────────────────────────────────
class RoleClubSerializer(serializers.ModelSerializer):

    # Affiche le libellé lisible ('Président') au lieu de la clé ('president')
    libelle_display = serializers.CharField(
        source='get_libelle_display',
        read_only=True
    )

    class Meta:
        model  = RoleClub
        fields = ['id', 'libelle', 'libelle_display', 'permissions', 'club']
        extra_kwargs = {
            # Le club est automatiquement déduit depuis l'URL, pas besoin
            # que le client l'envoie manuellement
            'club': {'read_only': True}
        }


# ──────────────────────────────────────────────────────────────────
# SERIALIZER CLUB — LECTURE (liste et détail)
# Utilisé pour afficher les informations d'un club.
# Contient des informations calculées (nombre_membres, etc.)
# ──────────────────────────────────────────────────────────────────
class ClubLectureSerializer(serializers.ModelSerializer):

    # Informations du créateur (lecture seule)
    createur        = UtilisateurProfilSerializer(read_only=True)

    # Statut lisible ('Validé' au lieu de 'valide')
    statut_display  = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )

    # Filière lisible
    filiere_display = serializers.CharField(
        source='get_filiere_display',
        read_only=True
    )

    # Champ calculé depuis la property du modèle
    nombre_membres  = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Club
        fields = [
            'id',
            'nom',
            'mission',
            'logo',
            'filiere',
            'filiere_display',
            'statut',
            'statut_display',
            'createur',
            'nombre_membres',
            'date_creation',
            'date_validation',
        ]


# ──────────────────────────────────────────────────────────────────
# SERIALIZER CLUB — CRÉATION
# Utilisé uniquement pour la création d'un club.
# Le créateur est automatiquement l'utilisateur connecté.
# Le statut est toujours EN_ATTENTE à la création.
# ──────────────────────────────────────────────────────────────────
class ClubCreationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Club
        fields = ['id', 'nom', 'mission', 'logo', 'filiere']
        # statut, createur, date_creation sont gérés automatiquement

    def create(self, validated_data):
        """
        Le créateur est automatiquement l'utilisateur connecté.
        Le statut est EN_ATTENTE par défaut (défini dans le modèle).
        """
        # request est passé dans le contexte depuis la view
        createur = self.context['request'].user

        club = Club.objects.create(
            **validated_data,
            createur=createur
        )
        return club


# ──────────────────────────────────────────────────────────────────
# SERIALIZER ADHÉSION — LECTURE
# Affiche les informations complètes d'une adhésion.
# ──────────────────────────────────────────────────────────────────
class AdhesionLectureSerializer(serializers.ModelSerializer):

    # Informations complètes du membre
    utilisateur = UtilisateurProfilSerializer(read_only=True)

    # Liste des rôles avec leurs détails
    roles_club  = RoleClubSerializer(many=True, read_only=True)

    # Informations de qui a ajouté ce membre
    ajoute_par  = UtilisateurProfilSerializer(read_only=True)

    class Meta:
        model  = Adhesion
        fields = [
            'id',
            'utilisateur',
            'club',
            'roles_club',
            'ajoute_par',
            'date_debut',
            'date_fin',
            'est_actif',
        ]


# ──────────────────────────────────────────────────────────────────
# SERIALIZER AJOUT DE MEMBRE
# Utilisé par le président pour ajouter un membre au club.
# Le président envoie l'email de l'utilisateur à ajouter
# et les rôles à lui attribuer.
# ──────────────────────────────────────────────────────────────────
class AjoutMembreSerializer(serializers.Serializer):
    """
    Ce serializer n'hérite pas de ModelSerializer car
    il combine des données de plusieurs modèles.
    """
    # Le président envoie l'email de la personne à ajouter
    email      = serializers.EmailField(
        help_text="Email de l'utilisateur à ajouter au club"
    )

    # Liste des IDs de rôles à attribuer (optionnel)
    roles_ids  = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list,
        help_text="Liste des IDs de rôles à attribuer"
    )

    def validate_email(self, value):
        """
        Vérifie que l'utilisateur avec cet email existe bien
        dans le système.
        """
        from accounts.models import Utilisateur
        try:
            utilisateur = Utilisateur.objects.get(email=value)
        except Utilisateur.DoesNotExist:
            raise serializers.ValidationError(
                "Aucun utilisateur trouvé avec cet email."
            )
        return value

    def validate_roles_ids(self, value):
        """
        Vérifie que les IDs de rôles envoyés existent bien
        et appartiennent au club concerné.
        Le club est passé dans le contexte depuis la view.
        """
        if not value:
            return value

        club = self.context.get('club')
        roles_valides = RoleClub.objects.filter(
            id__in=value,
            club=club
        )

        if roles_valides.count() != len(value):
            raise serializers.ValidationError(
                "Un ou plusieurs rôles sont invalides pour ce club."
            )
        return value


# ──────────────────────────────────────────────────────────────────
# SERIALIZER GESTION DES RÔLES D'UN MEMBRE
# Utilisé par le président pour modifier les rôles d'un membre.
# L'administrateur l'utilise aussi pour le transfert de président.
# ──────────────────────────────────────────────────────────────────
class GestionRolesSerializer(serializers.Serializer):
    """
    Permet de redéfinir complètement les rôles d'un membre.
    Envoyer une liste vide [] retire tous les rôles.
    """
    roles_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Nouvelle liste complète des IDs de rôles"
    )

    def validate_roles_ids(self, value):
        club = self.context.get('club')

        # Récupère l'utilisateur connecté depuis le contexte
        request = self.context.get('request')

        # Si ce n'est pas un admin, il ne peut pas attribuer
        # le rôle de président (transfert réservé à l'admin)
        if not request.user.est_administrateur:
            roles_president = RoleClub.objects.filter(
                id__in=value,
                club=club,
                libelle=RoleClub.PRESIDENT
            )
            if roles_president.exists():
                raise serializers.ValidationError(
                    "Seul l'administrateur peut transférer le rôle de président."
                )

        # Vérifie que tous les rôles appartiennent bien à ce club
        roles_valides = RoleClub.objects.filter(
            id__in=value,
            club=club
        )
        if roles_valides.count() != len(value):
            raise serializers.ValidationError(
                "Un ou plusieurs rôles sont invalides pour ce club."
            )
        return value