
// Correspond aux modèles Club, RoleClub et Adhesion
// définis dans clubs/models.py côté Django.

import { Utilisateur } from './utilisateur.model';

// Types stricts pour éviter les fautes de frappe
export type StatutClub =
  | 'en_attente'
  | 'valide'
  | 'suspendu'
  | 'archive';

export type FiliereClub =
  | 'genie_logiciel'
  | 'reseaux_telecom'
  | 'genie_civil'
  | 'comptabilite'
  | 'marketing'
  | 'toutes_filieres';

export type LibelleRole =
  | 'president'
  | 'secretaire'
  | 'tresorier'
  | 'membre';

// Correspond au modèle RoleClub Django
export interface RoleClub {
  id: number;
  libelle: LibelleRole;
  libelle_display: string; // Ex: "Président"
  permissions: string[];
  club: number;
}

// Correspond au modèle Club Django
// Retourné par ClubLectureSerializer
export interface Club {
  id: number;
  nom: string;
  mission: string;
  logo: string | null;
  filiere: FiliereClub;
  filiere_display: string;  // Ex: "Génie Logiciel"
  statut: StatutClub;
  statut_display: string;   // Ex: "Validé"
  createur: Utilisateur;
  nombre_membres: number;
  date_creation: string;
  date_validation: string | null;
}

// Correspond au modèle Adhesion Django
// Retourné par AdhesionLectureSerializer
export interface Adhesion {
  id: number;
  utilisateur: Utilisateur;
  club: number;
  roles_club: RoleClub[];   // ManyToMany → tableau de rôles
  ajoute_par: Utilisateur;
  date_debut: string;
  date_fin: string | null;
  est_actif: boolean;
}

// Corps de la requête pour créer un club
// POST /api/clubs/creer/
export interface ClubCreationRequest {
  nom: string;
  mission: string;
  filiere: FiliereClub;
  logo?: File | null;
}

// Corps de la requête pour ajouter un membre
// POST /api/clubs/<pk>/membres/ajouter/
export interface AjoutMembreRequest {
  email: string;
  roles_ids: number[];
}

// Corps de la requête pour gérer les rôles
// PUT /api/clubs/<pk>/membres/<user_pk>/roles/
export interface GestionRolesRequest {
  roles_ids: number[];
}