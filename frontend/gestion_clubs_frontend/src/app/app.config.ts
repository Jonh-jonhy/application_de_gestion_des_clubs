// Configuration globale de l'application Angular.
// Enregistre les providers nécessaires au démarrage.

import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { jwtInterceptor } from './core/interceptors/jwt.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Enregistre toutes les routes de l'application
    provideRouter(routes),

    // Active le client HTTP avec notre intercepteur JWT
    // withInterceptors() → nouvelle API Angular 19
    // pour les intercepteurs fonctionnels
    provideHttpClient(
      withInterceptors([jwtInterceptor])
    ),
  ]
};