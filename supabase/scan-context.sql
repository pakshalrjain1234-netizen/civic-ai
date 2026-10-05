-- Apply after schema.sql and evidence-integrity.sql, including on existing CivicEye databases.
alter table public.incident_reports add column if not exists scan_context jsonb not null default '{}'::jsonb;
create or replace function public.record_scan_context(p_id text,p_context jsonb) returns void language plpgsql security definer set search_path=public as $$declare c jsonb;coverage numeric;begin
if auth.uid() is null then raise exception 'Sign in required';end if;
if jsonb_typeof(p_context)<>'object' then raise exception 'Invalid scan metadata';end if;
if p_context->>'surfaceCoverage' is not null then coverage=(p_context->>'surfaceCoverage')::numeric;if coverage<0 or coverage>100 then raise exception 'Invalid estimated coverage';end if;end if;
if p_context->>'severity' not in ('LOW','MEDIUM','HIGH','CRITICAL') then raise exception 'Invalid scan severity';end if;
c=jsonb_build_object('source','camera-scan','capturedAt',(p_context->>'capturedAt')::timestamptz,'surfaceCoverage',coverage,'severity',p_context->>'severity','issueType',p_context->>'issueType','confidence',greatest(0,least(1,(p_context->>'confidence')::numeric)),'note','Vision endpoint estimate; canonical incident routing uses server-confirmed analysis');
update incident_reports set scan_context=c where incident_id=p_id and user_id=auth.uid();if not found then raise exception 'Only your submitted report can receive scan context';end if;end$$;
revoke all on function record_scan_context(text,jsonb) from public;grant execute on function record_scan_context(text,jsonb) to authenticated;
