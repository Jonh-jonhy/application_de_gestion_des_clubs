// src/app/features/auth/register/register.ts
//
// Page d'inscription — crée un nouveau compte utilisateur.
// Le rôle attribué par défaut est VISITEUR (côté Django).
// Utilise ReactiveForms avec validation croisée
// pour vérifier que les deux mots de passe correspondent.

import { Component, signal } from '@angular/core';
import { FormBuilder, FormGroup,
         Validators, ReactiveFormsModule,
         AbstractControl, ValidationErrors } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HeaderPublic } from '../../../shared/components/header-public/header-public';

import { AuthService } from '../../../core/services/auth.service';

// ── Validateur personnalisé ───────────────────────────────────────
// Vérifie que password et password2 sont identiques.
// Placé au niveau du groupe (pas d'un champ seul)
// car il a besoin d'accéder aux deux champs simultanément.
function motsDePasseIdentiques(
  group: AbstractControl
): ValidationErrors | null {
  const password  = group.get('password')?.value;
  const password2 = group.get('password2')?.value;
  return password === password2 ? null : { motsDePasse: true };
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, HeaderPublic],
  templateUrl: './register.html',
})
export class Register {

  // Visibilité des mots de passe (deux champs séparés)
  mdpVisible     = signal(false);
  mdpConfVisible = signal(false);

  // État de chargement pendant l'appel API
  chargement = signal(false);

  // Message d'erreur global retourné par Django
  erreur = signal<string | null>(null);

  formulaire: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.formulaire = this.fb.group({
      prenom: ['', [
        Validators.required,
        Validators.minLength(2)
      ]],
      nom: ['', [
        Validators.required,
        Validators.minLength(2)
      ]],
      email: ['', [
        Validators.required,
        Validators.email
      ]],
      password: ['', [
        Validators.required,
        Validators.minLength(8)
      ]],
      password2: ['', [
        Validators.required,
      ]],
    // Validateur de groupe : mots de passe identiques
    }, { validators: motsDePasseIdentiques });
  }

  // Getters pour accès facile dans le template
  get prenom()    { return this.formulaire.get('prenom');    }
  get nom()       { return this.formulaire.get('nom');       }
  get email()     { return this.formulaire.get('email');     }
  get password()  { return this.formulaire.get('password');  }
  get password2() { return this.formulaire.get('password2'); }

  toggleMdp():     void { this.mdpVisible.update(v => !v);     }
  toggleMdpConf(): void { this.mdpConfVisible.update(v => !v); }

  onSubmit(): void {
    if (this.formulaire.invalid) {
      this.formulaire.markAllAsTouched();
      return;
    }

    this.chargement.set(true);
    this.erreur.set(null);

    this.authService.register(this.formulaire.value).subscribe({
      next: () => {
        // Après inscription → redirige vers le dashboard
        // Le rôle est VISITEUR par défaut
        this.router.navigate(['/dashboard']);
        this.chargement.set(false);
      },
      error: (err) => {
        // Django retourne les erreurs par champ
        // Ex: { "email": ["Un utilisateur avec cet email existe déjà."] }
        const erreurs = err.error;
        if (erreurs?.email) {
          this.erreur.set(erreurs.email[0]);
        } else if (erreurs?.password) {
          this.erreur.set(erreurs.password[0]);
        } else {
          this.erreur.set('Une erreur est survenue. Réessayez.');
        }
        this.chargement.set(false);
      }
    });
  }

  annee = new Date().getFullYear();
}