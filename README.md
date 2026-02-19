# Link Generator SaaS

## Overview

This project is a SaaS-oriented web application built to manage user authentication, subscription plans (FREE and PRO), and controlled link generation.

The system follows a modern SPA architecture using React on the frontend and Supabase as Backend-as-a-Service (BaaS), leveraging PostgreSQL with Row Level Security (RLS) for fine-grained access control.

---

## Architecture

### Frontend Layer

- React (Vite)
- React Router (route management)
- Context API (global authentication state)
- Protected Route pattern (authorization guard)

The frontend is responsible for:

- Authentication flow
- Conditional rendering based on subscription plan
- Navigation control
- UI state management

---

### Backend Layer (Supabase)

- Python
- Fastapi
- Supabase Auth (JWT-based authentication)
- PostgreSQL database
- Row Level Security (RLS)
- SQL Triggers
- Access Policies

Supabase handles:

- Secure authentication
- User session management
- Data persistence
- Access control enforcement at database level

---

## Application Flow

### 1. Authentication

- User registers or logs in
- Supabase generates JWT
- Session is stored client-side

### 2. Profile Creation

A PostgreSQL trigger automatically creates a profile entry when a new user is inserted into `auth.users`.

Example:

```sql
create function public.handle_new_user()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into public.profiles (id, email, plan)
  values (new.id, new.email, 'free');
  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();
```
