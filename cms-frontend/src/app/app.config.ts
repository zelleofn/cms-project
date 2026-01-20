import { ApplicationConfig, provideBrowserGlobalErrorListeners, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router'
import { GraphQLModule, createApollo } from './graphql-module';
import { provideHttpClient } from '@angular/common/http'; 
import { provideAnimations } from '@angular/platform-browser/animations';
import { Apollo, APOLLO_OPTIONS } from 'apollo-angular';
import { HttpLink } from 'apollo-angular/http';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(),
    provideAnimations(),
    {
      provide: APOLLO_OPTIONS,
      useFactory: createApollo,
      deps: [HttpLink],
    },
    Apollo, 
    importProvidersFrom(GraphQLModule)
  ]
};