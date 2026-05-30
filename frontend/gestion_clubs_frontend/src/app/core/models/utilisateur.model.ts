export interface Utilisateur {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  // Les 3 rôles système définis dans notre modèle Django
  role: 'visiteur' | 'membre' | 'administrateur';
  photo_profil: string | null;
  date_inscription: string;
}

// Réponse complète du endpoint POST /api/auth/register/
// et POST /api/auth/login/
export interface AuthResponse {
  message: string;
  utilisateur: Utilisateur;
  tokens: {
    access: string;   // Token court (1 jour) → envoyé à chaque requête
    refresh: string;  // Token long (7 jours) → utilisé pour renouveler
  };
}

// Corps de la requête POST /api/auth/login/
export interface LoginRequest {
  email: string;
  password: string;
}

// Corps de la requête POST /api/auth/register/
export interface RegisterRequest {
  email: string;
  nom: string;
  prenom: string;
  password: string;
  password2: string; // Confirmation côté Django
}