// src/app/core/models/publication.model.ts
//
// Correspond au modèle Publication Django.

import { Utilisateur } from './utilisateur.model';

export type StatutPublication =
  | 'en_attente'
  | 'publiee'
  | 'rejetee'
  | 'archivee';

// Retourné par PublicationLectureSerializer
export interface Publication {
  id: number;
  titre: string;
  description: string;
  image: string | null;
  date_debut: string | null;  // Présent si c'est un événement
  date_fin: string | null;    // Présent si c'est un événement
  est_evenement: boolean;     // Property calculée côté Django
  statut: StatutPublication;
  statut_display: string;
  motif_rejet: string | null; // Rempli par l'admin en cas de rejet
  club: number;
  club_nom: string;
  auteur: Utilisateur;
  date_creation: string;
  date_validation: string | null;
}

// Corps de la requête pour créer une publication
// POST /api/clubs/<pk>/publications/creer/
export interface PublicationCreationRequest {
  titre: string;
  description: string;
  image?: File | null;
  date_debut?: string | null;
  date_fin?: string | null;
}

// Corps de la requête pour valider/rejeter
// POST /api/clubs/publications/<pub_pk>/valider/
export interface ValidationPublicationRequest {
  action: 'publier' | 'rejeter';
  motif_rejet?: string;
}