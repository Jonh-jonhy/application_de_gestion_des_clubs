import { TestBed } from '@angular/core/testing';

import { Club } from './club';

describe('Club', () => {
  let service: Club;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Club);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
