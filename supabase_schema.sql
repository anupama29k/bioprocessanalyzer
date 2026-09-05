-- SYNAPSE — Supabase schema
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New query)
--
-- NOTE: The actual tables in Supabase are `batches` and `process_measurements`
-- using a generic key-value measurement pattern (parameter_name, value, unit).
-- The schema below documents both the original design and the live schema.

-- ═══════════════════════════════════════════════════════════════════════════════
-- 1. batches — one row per fermentation run
-- ═══════════════════════════════════════════════════════════════════════════════
create table if not exists batches (
    id              uuid default gen_random_uuid() primary key,
    batch_code      text not null unique,
    organism        text default '',
    product_type    text default '',
    scale_liters    double precision,
    start_date      date,
    end_date        date,
    notes           text default '',
    created_at      timestamptz default now(),

    -- Run Manager extended fields (v2)
    vessel          text default '',
    operator        text default '',
    golden_batch_ref text default '',
    protocol_notes  text default '',
    outcome         text default ''
);

-- Migration helpers (safe to re-run — adds columns only if missing)
alter table batches add column if not exists vessel text default '';
alter table batches add column if not exists operator text default '';
alter table batches add column if not exists golden_batch_ref text default '';
alter table batches add column if not exists protocol_notes text default '';
alter table batches add column if not exists outcome text default '';

-- ═══════════════════════════════════════════════════════════════════════════════
-- 2. process_measurements — generic key-value time-series
-- ═══════════════════════════════════════════════════════════════════════════════
create table if not exists process_measurements (
    id                bigint generated always as identity primary key,
    batch_id          uuid references batches(id) on delete cascade,
    parameter_name    text not null,
    value             double precision,
    unit              text default '',
    day_of_run        double precision default 0,
    instrument        text default '',
    instrument_source text default '',     -- 'online' (Pulse) or 'offline' (manual)
    created_at        timestamptz default now()
);

-- Migration helpers
alter table process_measurements add column if not exists instrument text default '';
alter table process_measurements add column if not exists instrument_source text default '';

-- Index for fast batch lookups
create index if not exists idx_measurements_batch
    on process_measurements (batch_id, day_of_run);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 3. Row-Level Security — allow anon key to read/write
-- ═══════════════════════════════════════════════════════════════════════════════
alter table batches enable row level security;
alter table process_measurements enable row level security;

-- NOTE: Use "create policy if not exists" or drop-and-recreate to avoid errors
-- on re-run. The statements below will error if policies already exist.
-- Wrap in DO block for safety:
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'anon_batches_all') THEN
        CREATE POLICY anon_batches_all ON batches FOR ALL USING (true) WITH CHECK (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'anon_measurements_all') THEN
        CREATE POLICY anon_measurements_all ON process_measurements FOR ALL USING (true) WITH CHECK (true);
    END IF;
END $$;
