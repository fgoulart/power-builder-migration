import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-home',
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  private readonly api = inject(ApiService);

  readonly title = signal('Power Builder Migration');
  readonly apiStatus = signal<string | null>(null);
  readonly apiEnvironment = signal<string | null>(null);
  readonly apiError = signal<string | null>(null);

  ngOnInit(): void {
    this.api.getHealth().subscribe({
      next: (response) => {
        this.apiStatus.set(response.status);
        this.apiEnvironment.set(response.environment);
      },
      error: () => {
        this.apiError.set('Backend indisponível. Inicie com: npm run backend');
      },
    });
  }
}
