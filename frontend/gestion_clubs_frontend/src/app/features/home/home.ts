// src/app/features/home/home.ts
//
// Page d'accueil publique — accessible sans connexion.
// Affiche le hero, les statistiques et le footer.
// Les stats seront dynamiques plus tard via l'API.

import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { HeaderPublic } from '../../shared/components/header-public/header-public';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink, HeaderPublic],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home {

  // Statistiques affichées sous les boutons CTA
  // Seront remplacées par des données réelles de l'API
  stats = [
    { valeur: '6',   label: 'Clubs actifs'     },
    { valeur: '50+', label: 'Membres inscrits'  },
    { valeur: '6',   label: 'Filières'          },
  ];

  annee = new Date().getFullYear();
}