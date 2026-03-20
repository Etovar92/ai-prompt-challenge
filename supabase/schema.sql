-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  TechQuest GenAI Prompt Challenge — Supabase Schema             ║
-- ║  Run this entire file in the Supabase SQL Editor                ║
-- ╚══════════════════════════════════════════════════════════════════╝

-- ── SUBMISSIONS ──────────────────────────────────────────────────────────────
create table if not exists public.submissions (
  id           uuid        primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  author_name  text        not null check (char_length(author_name)  between 1 and 100),
  ai_tool      text        not null,
  description  text        not null check (char_length(description)  between 1 and 300),
  prompt_text  text        not null check (char_length(prompt_text)  between 1 and 2000)
);

-- ── REACTIONS ────────────────────────────────────────────────────────────────
create table if not exists public.reactions (
  id            uuid        primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  submission_id uuid        not null references public.submissions(id) on delete cascade,
  emoji         text        not null check (char_length(emoji) between 1 and 10),
  browser_id    text        not null check (char_length(browser_id) between 1 and 200),
  unique (submission_id, emoji, browser_id)
);

-- Drop old emoji allow-list constraint if it exists (allows any emoji now)
alter table public.reactions drop constraint if exists reactions_emoji_check;

-- ── CATEGORY COLUMN ───────────────────────────────────────────────────────────────
alter table public.submissions add column if not exists category text
  check (category in ('planning','writing','summarizing','comparing','templates','brainstorming','other'));

-- ── POLL VOTES ───────────────────────────────────────────────────────────────
create table if not exists public.poll_votes (
  id          uuid        primary key default gen_random_uuid(),
  created_at  timestamptz not null default now(),
  option_key  text        not null check (option_key in (
                'planning','writing','summarizing','comparing','templates','brainstorming'
              )),
  browser_id  text        not null check (char_length(browser_id) between 1 and 200),
  unique (browser_id)   -- one vote per browser
);

-- ── ROW LEVEL SECURITY ───────────────────────────────────────────────────────
alter table public.submissions enable row level security;
alter table public.reactions    enable row level security;
alter table public.poll_votes   enable row level security;

-- Submissions: public read + insert + delete (admin password enforced client-side)
drop policy if exists "public read submissions"   on public.submissions;
drop policy if exists "public insert submissions" on public.submissions;
drop policy if exists "public delete submissions" on public.submissions;
create policy "public read submissions"   on public.submissions for select using (true);
create policy "public insert submissions" on public.submissions for insert with check (true);
create policy "public delete submissions" on public.submissions for delete using (true);

-- Reactions: public read + insert + delete (supports toggling reactions)
drop policy if exists "public read reactions"   on public.reactions;
drop policy if exists "public insert reactions" on public.reactions;
drop policy if exists "public delete reactions" on public.reactions;
create policy "public read reactions"    on public.reactions for select using (true);
create policy "public insert reactions"  on public.reactions for insert with check (true);
create policy "public delete reactions"  on public.reactions for delete using (true);

-- Poll votes: public read + insert + delete (delete needed for admin reset)
drop policy if exists "public read poll_votes"   on public.poll_votes;
drop policy if exists "public insert poll_votes" on public.poll_votes;
drop policy if exists "public delete poll_votes" on public.poll_votes;
create policy "public read poll_votes"   on public.poll_votes for select using (true);
create policy "public insert poll_votes" on public.poll_votes for insert with check (true);
create policy "public delete poll_votes" on public.poll_votes for delete using (true);

-- ── COMMENTS ─────────────────────────────────────────────────────────────────
create table if not exists public.comments (
  id            uuid        primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  submission_id uuid        not null references public.submissions(id) on delete cascade,
  author_name   text        not null check (char_length(author_name) between 1 and 100),
  body          text        not null check (char_length(body) between 1 and 600)
);

alter table public.comments enable row level security;
drop policy if exists "public read comments"   on public.comments;
drop policy if exists "public insert comments" on public.comments;
create policy "public read comments"   on public.comments for select using (true);
create policy "public insert comments" on public.comments for insert with check (true);
