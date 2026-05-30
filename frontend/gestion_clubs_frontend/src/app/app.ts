
// Composant racine de l'application.
// RouterOutlet est nécessaire pour afficher
// les composants selon la route active.

import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],  // ← nécessaire pour le routing
  template: `<router-outlet />`,  // ← affiche le composant de la route active
})
export class App {}