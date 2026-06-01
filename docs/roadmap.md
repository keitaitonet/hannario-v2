# Roadmap

This roadmap follows the handoff document. It records the current practical
state of the project, not a promise to build every possible feature.

## Phase 0: Heart And Mouth

Status: done.

Implemented:

- Letta agent creation
- persona and playbook blocks
- Discord shell with `on_message -> Letta -> reply`
- `!ping`
- fallback reply when Letta fails

## Phase 1: Memory And Self-Revision

Status: mostly done, intentionally conservative.

Implemented:

- playbook memory
- memory snapshots
- memory write audit log
- curator dry-run scripts
- LLM curator proposal script
- manual playbook append flow
- curator proposal from mention logs
- curator proposal from internal schedule results

Still open:

- automatic curator apply
- enforced read-only memory blocks with a strict write gate
- periodic playbook deduplication and cleanup

Current stance: keep this human-reviewed until memory drift becomes a real
problem.

## Phase 2: Body Clock

Status: implemented and being tuned.

Implemented:

- heartbeat loop
- private heartbeat Letta consult
- proactive `consider_reply` decision
- heartbeat post cooldown
- stale observation filtering
- heartbeat treats observations as untrusted
- random participation
- active follow-up replies
- silence phrases
- SQLite scheduled tasks
- direct simple relative schedules like "10分後に..."
- Discord schedule tools
- internal schedule tasks (`think`, `observe`, `follow_up`)
- internal future-self reflection stored in schedule logs

Still open:

- better cheap gate before full heartbeat Letta consult
- better heuristics for when proactive participation is socially useful
- production tuning for intervals and cooldowns

## Phase 3: Organ Expansion

Status: minimum viable organs are implemented.

Implemented:

- Discord observation tools
- schedule tools
- `get_recent_discord_internal_results`
- `run_readonly_sql`
- `fetch_web_text`
- unified tool registration script

Still open:

- richer Discord write tools
- writable DB tools, if ever needed
- broader web search or source-aware browsing
- playbook rules for when to use DB/web/internal-result tools

Current stance: keep DB and web conservative. Read-only is enough for now.

## Phase 4: Survival And Safety

Status: not implemented.

Needed before unattended deployment:

- process supervision on the target server
- automatic restart
- log rotation
- backup plan for Letta data, SQLite, logs, and memory snapshots
- cost guardrails
- production `.env` profile
- deployment checklist

Explicitly still out of scope:

- arbitrary shell tool
- self-modifying source code
- VM/computer-use style automation
- RL-based memory control
- whole-playbook automatic consolidation

## Near-Term Recommendation

The bot is ready for limited deployment testing, but not yet for careless
always-on operation.

Recommended next steps:

1. Clean up docs and `.env.example`.
2. Decide the home-server supervision method.
3. Add deployment notes for that method.
4. Run one short supervised session.
5. Tune heartbeat, random participation, and schedule settings.
6. Only then move to longer unattended runs.
