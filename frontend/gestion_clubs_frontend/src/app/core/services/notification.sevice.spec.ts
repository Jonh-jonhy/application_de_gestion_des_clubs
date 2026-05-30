import { TestBed } from '@angular/core/testing';

import { NotificationSevice } from './notification.sevice';

describe('NotificationSevice', () => {
  let service: NotificationSevice;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NotificationSevice);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
