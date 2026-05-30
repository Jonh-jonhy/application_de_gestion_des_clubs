import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Creer } from './creer';

describe('Creer', () => {
  let component: Creer;
  let fixture: ComponentFixture<Creer>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Creer],
    }).compileComponents();

    fixture = TestBed.createComponent(Creer);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
