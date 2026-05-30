// Protège les routes réservées à l'administrateur.
// Si l'utilisateur n'est pas admin → redirige vers /dashboard.
// Utilisé sur : /admin, /admin/clubs, /admin/publications.

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const adminGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.estAdmin()) {
    // Administrateur → accès autorisé
    return true;
  }

  if (authService.estConnecte()) {
    // Connecté mais pas admin → redirige vers son dashboard
    return router.createUrlTree(['/dashboard']);
  }

  // Non connecté → redirige vers login
  return router.createUrlTree(['/login']);
};