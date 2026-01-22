import 'zone.js';
import 'zone.js/testing';
import { beforeAll } from '@jest/globals';
import { TestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting,
} from '@angular/platform-browser-dynamic/testing';

import { provideRouter } from '@angular/router';
import { ApolloTestingModule } from 'apollo-angular/testing';

TestBed.initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting(),
);


beforeAll(() => {
  TestBed.configureTestingModule({
    imports: [ApolloTestingModule],
    providers: [provideRouter([])],
  });
});
