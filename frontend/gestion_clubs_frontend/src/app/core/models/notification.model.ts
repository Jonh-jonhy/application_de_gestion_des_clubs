// src/app/core/models/notification.model.ts
//
// Correspond au modèle Notification Django.

export type TypeNotification =
  | 'club_soumis'
  | 'club_valide'
  | 'club_rejete'
  | 'club_suspendu'
  | 'publication_soumise'
  | 'publication_validee'
  | 'publication_rejetee'
  | 'membre_ajoute';

export interface Notification {
  id: number;
  type_notification: TypeNotification;
  type_display: string;
  titre: string;
  message: string;
  est_lue: boolean;
  date_creation: string;
}