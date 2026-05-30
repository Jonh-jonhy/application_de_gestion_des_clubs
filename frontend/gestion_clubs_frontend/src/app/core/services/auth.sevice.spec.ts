import { TestBed } from '@angular/core/testing';

import { AuthSevice } from './auth.sevice';

describe('AuthSevice', () => {
  let service: AuthSevice;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthSevice);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
