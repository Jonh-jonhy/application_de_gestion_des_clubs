
// Service central d'authentification.
// Gère : login, register, logout, stockage des tokens,
// et expose l'utilisateur connecté à toute l'application
// via un signal 

import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environement';
import {
  Utilisateur,
  AuthResponse,
  LoginRequest,
  RegisterRequest
} from '../models/utilisateur.model';

@Injectable({
  // providedIn: 'root' → une seule instance pour toute l'app
  // (pattern Singleton)
  providedIn: 'root'
})
export class AuthService {

  // ── URL de base ───────────────────────────────────────────────
  private readonly apiUrl = `${environment.apiUrl}/auth`;

  // ── Signal utilisateur connecté ───────────────────────────────
  // Signal = valeur réactive d'Angular 19
  // Quand il change, tous les composants qui l'utilisent
  // se mettent à jour automatiquement
  private _utilisateur = signal<Utilisateur | null>(
    this.chargerUtilisateurLocal()
  );

  // ── Computed signals (valeurs dérivées) ───────────────────────
  // computed() recalcule automatiquement quand _utilisateur change

  // Utilisateur courant — lecture seule depuis l'extérieur
  readonly utilisateur = this._utilisateur.asReadonly();

  // Vrai si un utilisateur est connecté
  readonly estConnecte = computed(() => this._utilisateur() !== null);

  // Vrai si l'utilisateur est administrateur
  readonly estAdmin = computed(
    () => this._utilisateur()?.role === 'administrateur'
  );

  // Vrai si l'utilisateur est membre ou admin
  readonly estMembre = computed(
    () => this._utilisateur()?.role === 'membre' ||
          this._utilisateur()?.role === 'administrateur'
  );

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  // ── INSCRIPTION ───────────────────────────────────────────────
  // POST /api/auth/register/
  register(donnees: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(
      `${this.apiUrl}/register/`,
      donnees
    ).pipe(
      tap(response => {
        // Après inscription : on stocke les tokens et l'utilisateur
        this.sauvegarderSession(response);
      })
    );
  }

  // ── CONNEXION ─────────────────────────────────────────────────
  // POST /api/auth/login/
  login(donnees: LoginRequest): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/login/`,
      donnees
    ).pipe(
      tap(response => {
        // simplejwt retourne access + refresh directement
        // sans objet "utilisateur" → on appelle /me/ ensuite
        this.sauvegarderTokens(response.access, response.refresh);
        // Charge le profil utilisateur depuis /me/
        this.chargerProfil().subscribe();
      })
    );
  }

  // ── PROFIL UTILISATEUR CONNECTÉ ───────────────────────────────
  // GET /api/auth/me/
  chargerProfil(): Observable<Utilisateur> {
    return this.http.get<Utilisateur>(
      `${this.apiUrl}/me/`
    ).pipe(
      tap(utilisateur => {
        // Met à jour le signal avec les données fraîches
        this._utilisateur.set(utilisateur);
        // Sauvegarde en localStorage pour persister entre les onglets
        localStorage.setItem('utilisateur', JSON.stringify(utilisateur));
      })
    );
  }

  // ── DÉCONNEXION ───────────────────────────────────────────────
  // POST /api/auth/logout/
  logout(): void {
    const refreshToken = localStorage.getItem('refresh_token');

    if (refreshToken) {
      // Blackliste le refresh token côté Django
      this.http.post(`${this.apiUrl}/logout/`, {
        refresh: refreshToken
      }).subscribe({
        error: () => {
          // Même en cas d'erreur, on nettoie le localStorage
          console.warn('Erreur lors du logout côté serveur');
        }
      });
    }

    // Nettoyage local dans tous les cas
    this.nettoyerSession();
    this.router.navigate(['/']);
  }

  // ── GETTERS TOKENS ────────────────────────────────────────────
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  // ── MÉTHODES PRIVÉES ──────────────────────────────────────────

  // Sauvegarde tokens + utilisateur après login/register
  private sauvegarderSession(response: AuthResponse): void {
    this.sauvegarderTokens(
      response.tokens.access,
      response.tokens.refresh
    );
    this._utilisateur.set(response.utilisateur);
    localStorage.setItem(
      'utilisateur',
      JSON.stringify(response.utilisateur)
    );
  }

  // Sauvegarde uniquement les tokens
  private sauvegarderTokens(access: string, refresh: string): void {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  }

  // Nettoie tout le localStorage à la déconnexion
  private nettoyerSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('utilisateur');
    this._utilisateur.set(null);
  }

  // Récupère l'utilisateur depuis localStorage au démarrage
  // (persiste la session après rafraîchissement de la page)
  private chargerUtilisateurLocal(): Utilisateur | null {
    const data = localStorage.getItem('utilisateur');
    return data ? JSON.parse(data) : null;
  }
}