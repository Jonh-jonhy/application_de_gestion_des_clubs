// src/app/features/auth/login/login.ts
//
// Page de connexion.
// Utilise ReactiveForms pour la validation des champs.
// Après connexion réussie, redirige selon le rôle :
// → admin : /admin
// → membre/visiteur : /dashboard

import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup,
         Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HeaderPublic } from '../../../shared/components/header-public/header-public';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, HeaderPublic],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  // Signal pour afficher/masquer le mot de passe
  motDePasseVisible = signal(false);

  // Signal pour l'état de chargement (pendant l'appel API)
  chargement = signal(false);

  // Signal pour afficher le message d'erreur
  erreur = signal<string | null>(null);

  // Formulaire réactif avec validation
  formulaire: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    // Initialisation du formulaire avec validateurs
    this.formulaire = this.fb.group({
      email: ['', [
        Validators.required,
        Validators.email
      ]],
      password: ['', [
        Validators.required,
        Validators.minLength(8)
      ]],
    });
  }

  // Getter pour accéder facilement aux champs dans le template
  get email() { return this.formulaire.get('email'); }
  get password() { return this.formulaire.get('password'); }

  // Bascule la visibilité du mot de passe
  toggleMotDePasse(): void {
    this.motDePasseVisible.update(v => !v);
  }

  // Soumission du formulaire
  onSubmit(): void {
    // Arrête si le formulaire est invalide
    if (this.formulaire.invalid) {
      this.formulaire.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.erreur.set(null);

    this.authService.login(this.formulaire.value).subscribe({
      next: () => {
        // Redirection selon le rôle après chargement du profil
        // On attend un tick pour que le signal utilisateur
        // soit mis à jour par chargerProfil()
        setTimeout(() => {
          if (this.authService.estAdmin()) {
            this.router.navigate(['/admin']);
          } else {
            this.router.navigate(['/dashboard']);
          }
          this.chargement.set(false);
        }, 500);
      },
      error: (err) => {
        // Affiche le message d'erreur Django
        this.erreur.set(
          err.error?.detail ||
          'Email ou mot de passe incorrect.'
        );
        this.chargement.set(false);
      }
    });
  }

  annee = new Date().getFullYear();
}