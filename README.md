# Headless CMS - Full Stack Application

Full-stack Headless CMS built with Angular frontend and Flask GraphQL backend, powered by WordPress as a datasource(Content published via WordPress sites). WordPress content is consumed via a GraphQL API and displayed through a custom Angular interface. WordPress serves as the content database, then pulled via WPGraphQL into the Flask backend, cached with Redis, and served to the Angular frontend.

## Live Demo

**Frontend:** https://cms-project-tan.vercel.app

## Tech Stack

### Frontend
- Angular 18
- TypeScript
- Apollo Client (GraphQL)
- Angular Material
- Vercel (Hosting)

### Backend
- Python (Flask)
- GraphQL (Graphene)
- PostgreSQL (Supabase, User Authentication)
- MySQL (Wordpress, Content Management)
- Redis (Caching)
- Render (Hosting)

### CMS
- WordPress (Pantheon)
- WPGraphQL
- Advanced Custom Fields (ACF)

### Infrastructure
- Docker, DockerHub, Kubernetes
- GitHub Actions (CI/CD)
- Supabase (Database)
- Redis Cloud (Caching)
- Agile WorkFlow (Jira)

### QA & Testing
- Puppeteer
- Jest
- PyTest
