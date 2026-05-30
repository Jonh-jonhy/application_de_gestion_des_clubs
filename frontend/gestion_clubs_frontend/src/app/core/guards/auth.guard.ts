// Protège les routes qui nécessitent d'être connecté.
// Si l'utilisateur n'est pas connecté → redirige vers /login.
// Utilisé sur : /dashboard, /clubs, /notifications, etc.

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estConnecte()) { 
    // Utilisateur connecté → accès autorisé
    return true;
  }

  // Non connecté → redirection vers la page de connexion
  return router.createUrlTree(['/login']);
};