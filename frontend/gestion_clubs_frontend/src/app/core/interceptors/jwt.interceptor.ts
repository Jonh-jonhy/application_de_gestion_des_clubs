
// Intercepteur HTTP fonctionnel.
// Son rôle : ajouter automatiquement le token JWT
// dans le header Authorization de CHAQUE requête HTTP.

import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {

  // inject() → nouvelle façon d'injecter dans les fonctions
  const authService = inject(AuthService);
  const token = authService.getAccessToken();

  // Si un token existe, on clone la requête avec le header
  // On clone car les requêtes HTTP sont immutables
  if (token) {
    const reqAvecToken = req.clone({
      setHeaders: {
        // Format attendu par notre backend Django
        Authorization: `Bearer ${token}`
      }
    });
    return next(reqAvecToken);
  }

  // Pas de token → requête publique, on la laisse passer
  return next(req);
};