import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header-public',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './header-public.html',
  styleUrl: './header-public.css',
})
export class HeaderPublic {
  menuOuvert = false;

  toggleMenu(): void {
    this.menuOuvert = !this.menuOuvert;
  }
}
