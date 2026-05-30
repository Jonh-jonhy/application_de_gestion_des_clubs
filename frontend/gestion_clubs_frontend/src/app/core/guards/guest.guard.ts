// Empêche un utilisateur déjà connecté d'accéder
// aux pages de login et register.
// Si connecté → redirige vers le bon dashboard selon le rôle.

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const guestGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.estConnecte()) {
    // Non connecté → peut accéder à login/register
    return true;
  }

  // Déjà connecté → redirige selon le rôle
  if (authService.estAdmin()) {
    return router.createUrlTree(['/admin']);
  }

  return router.createUrlTree(['/dashboard']);
};