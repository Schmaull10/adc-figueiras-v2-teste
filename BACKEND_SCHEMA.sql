-- ADC Figueiras V2 — rascunho de modelo relacional para futuro backend (ex.: PostgreSQL/Supabase)
-- IMPORTANTE: estrutura de referência. Rever RLS/políticas de segurança antes de produção.

create table seasons (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  is_active boolean not null default false,
  archived boolean not null default false,
  created_at timestamptz not null default now()
);

create table profiles (
  id uuid primary key,
  display_name text not null,
  email text,
  member_number text,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table user_roles (
  user_id uuid not null references profiles(id) on delete cascade,
  role text not null check (role in ('player','staff','admin','member')),
  primary key (user_id, role)
);

create table players (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid references profiles(id) on delete set null,
  name text not null,
  position text,
  shirt_number text,
  status text default 'Disponível',
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table trainings (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id),
  training_date date not null,
  training_time time,
  location text,
  notes text,
  created_at timestamptz not null default now()
);

create table training_entries (
  training_id uuid not null references trainings(id) on delete cascade,
  player_id uuid not null references players(id) on delete cascade,
  attendance_status text,
  weight_pre numeric(6,2),
  weight_post numeric(6,2),
  primary key(training_id, player_id)
);

create table games (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id),
  game_date date not null,
  game_time time,
  opponent text not null,
  home_away text not null check (home_away in ('Casa','Fora')),
  competition text,
  venue text,
  status text not null default 'scheduled' check (status in ('scheduled','live','final')),
  figueiras_score integer,
  opponent_score integer,
  created_at timestamptz not null default now()
);

create table game_roster (
  game_id uuid not null references games(id) on delete cascade,
  player_id uuid not null references players(id) on delete cascade,
  status text not null default 'Não convocado',
  primary key(game_id, player_id)
);

create table match_events (
  id uuid primary key default gen_random_uuid(),
  game_id uuid not null references games(id) on delete cascade,
  event_type text not null check (event_type in ('goal','yellow','red','halftime','note')),
  minute integer,
  player_id uuid references players(id),
  assist_player_id uuid references players(id),
  note text,
  created_at timestamptz not null default now()
);

create table standings (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id),
  competition text,
  team text not null,
  played integer default 0,
  wins integer default 0,
  draws integer default 0,
  losses integer default 0,
  goals_for integer default 0,
  goals_against integer default 0,
  points integer default 0
);

create table fines (
  id uuid primary key default gen_random_uuid(),
  season_id uuid not null references seasons(id),
  player_id uuid not null references players(id),
  fine_date date not null,
  reason text not null,
  amount numeric(8,2) not null,
  paid boolean not null default false
);

create table notifications (
  id uuid primary key default gen_random_uuid(),
  notification_type text not null,
  title text not null,
  body text not null,
  audience text not null,
  game_id uuid references games(id) on delete cascade,
  player_id uuid references players(id) on delete cascade,
  trigger_type text,
  scheduled_at timestamptz,
  sent_at timestamptz,
  created_at timestamptz not null default now()
);

create table push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  endpoint text not null unique,
  subscription_json jsonb not null,
  created_at timestamptz not null default now()
);

create table join_requests (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null,
  requested_role text not null check (requested_role in ('player','member')),
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

-- A fase de produção deverá ativar RLS e definir políticas explícitas.
-- Exemplos de regras a desenhar:
-- 1) dados públicos: jogos/resultados/classificação/estatísticas públicas;
-- 2) jogadores autenticados: pesagens conforme política do clube + treinos/convocatórias;
-- 3) staff: escrita em treinos, pesagens, jogos e Match Center;
-- 4) admin: utilizadores, funções, épocas e configurações;
-- 5) multas e outros dados internos não são públicos;
-- 6) notificações individuais só podem ser lidas pelo destinatário e staff/admin.
