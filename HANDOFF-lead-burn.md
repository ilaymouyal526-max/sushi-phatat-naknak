# HANDOFF: lead burn (`/lead-burn` + `lead-finder` subagent)

Handoff from the session of 24 Nov 2026. To continue in a new session, say:
**"Read `HANDOFF-lead-burn.md` and continue the lead burn."**
The lead finder itself (what `find`, `merge`, `plan` and the rest do) is covered in [`HANDOFF-lead-finder.md`](HANDOFF-lead-finder.md). This file covers only the leftover-usage scheduler built on top of it.

## Start here
- **Branch:** `claude/wizardly-allen-y5msa0` (repo `ilaymouyal526-max/sushi-phatat-naknak`, which is **public**). Everything is committed and pushed there.
  It includes the whole lead finder, merged from `claude/jolly-meitner-s4e01m`. No pull request has been opened.
- **Tests:** `python3 -m unittest discover -s tests` runs 51 tests: the 43 lead-finder tests plus 8 in `tests/test_burn.py`. All pass.
- **Spending rule (CLAUDE.md):** never spend tokens, credits or money without a clear yes. A lead-burn run spends plan usage,
  so it **only runs after the user replies "go" for that specific window**. No reply means no run.

## What the user asked for
> "Make it a subagent that uses credits an hour before the reset times. If there are still a lot of credits to use, ask for
> permission and send me a notification beforehand, in case I have some other project to work on."

Here "credits" means the Claude plan's usage window, which resets every 5 hours. Usage left over at the reset is lost.

## How it works
1. **Scheduled check.** A one-shot `send_later` message named `lead-burn check`, with the text `/lead-burn check`, fires into
   the session. Only one check is ever pending: each check deletes any other pending ones and schedules the next.
2. **Reading the window.** The check calls `get_session` (claude-code-remote) and reads `external_metadata.rate_limit_info`:
   `resetsAt` (epoch seconds), `status` (`allowed` / `allowed_warning` / `rejected`), `isUsingOverage` and `rateLimitType`.
3. **Decision.** `python3 -m lead_agent burn decide --resets-at <epoch> --status <status> [--overage]` returns one of:
   - `wait`: it's too early (more than 85 min before the reset), there is no reset time yet, or the user was already asked.
     The next check is scheduled at reset − 70 min.
   - `skip`: usage is low (a warning status or overage), fewer than 25 min are left, or it's quiet hours (23:00–08:00 Israel time).
     The next check is scheduled 70 min before the end of the *next* window (reset + 230 min).
   - `notify`: the status is `allowed`, there's no overage, and the reset is close. The check runs `burn asked <resetsAt>`,
     sends a **PushNotification**, posts the same question in the chat (`go` / `go <city> <category> <count>` / `skip`),
     schedules the next check, and **waits**.
   - `off`: the scheduler is disabled, so nothing is scheduled.
4. **On "go".** The session re-checks that at least 25 min are left, then starts the **`lead-finder`** subagent in the foreground
   with the city, category, `verify_count` and a deadline (reset − 5 min, Israel time). When the subagent returns:
   - `burn finish --run <run.json> --resets-at <epoch>` records the run and moves the rotation on;
   - **SendUserFile** sends the `.html` phone page and the `.xlsx`. The container's `leads/` folder doesn't survive a restart,
     so this is how the user keeps the files;
   - a "done" push notification goes out, and the top-10 table appears in the chat;
   - `lead_agent/state/burn.json` (only) is committed and pushed.

## Files
| Path | Role |
|---|---|
| `.claude/agents/lead-finder.md` | Subagent: one find → verify → Hebrew texts → merge run, checking the clock every 5 leads and stopping at the deadline |
| `.claude/skills/lead-burn/SKILL.md` | The `/lead-burn` workflow: `check`, `go`, `skip`, `status`, `on`, `off`, `set` |
| `lead_agent/burn.py` | `decide`, rotation, `mark_asked`, `finish`, hashed memory, `status`, `configure` |
| `lead_agent/cli.py` | `burn decide|asked|target|finish|status|set`. `find` also skips leads in the hashed seen/dnc lists |
| `lead_agent/state/burn.json` | **Committed** state: settings, rotation index, `asked_for`, run counts, hashed `seen`/`dnc` ids. Override the path with `$LEAD_BURN_STATE` |
| `tests/test_burn.py` | Covers the decide branches, quiet hours, a check that no lead data reaches the state file, `find` skipping remembered leads, and the CLI |

## Defaults (change with `python3 -m lead_agent burn set …`)
| Setting | Default | Flag |
|---|---|---|
| Ask this long before the reset | 70 min | `--notify-before` |
| Stop the run before the reset | 5 min | (in `burn.json`) |
| Don't ask if less is left | 25 min | (in `burn.json`) |
| Quiet hours (Israel time) | 23:00–08:00 | `--quiet 23:00-08:00` |
| Leads verified per run | 40 | `--verify-count` |
| On/off | on | `--enabled on\|off` |
| Rotation | 16 cities × beauty, health, trades, auto, fitness, professional (96 targets, grouped by category) | edit `targets` in `burn.json` |

## Privacy decisions (the repo is public)
- `leads/` stays git-ignored. **Never commit run files, phone lists or the call log.**
- `burn.json` stores only salted SHA-256 hashes (16 hex characters) of **lead ids**. Phones are never stored, not even hashed,
  because a hashed phone number can be reversed by trying every number. A test checks that no name, phone or `osm:` id
  ends up in the state file.
- These hashed lists let `find` skip leads delivered by earlier burn runs, and businesses that said no, even after the
  container is wiped. The do-not-contact list is copied from `leads/do_not_contact.csv` each time `burn finish` runs.

## Current status (24 Nov 2026, ~10:40 UTC)
- The **first check is armed**: trigger `trig_01EFzncC73Q6BYJTiJn3s6Qz`, which fires at **2026-11-24 14:10 UTC (16:10 Israel time)**,
  70 min before the window resets at 17:20 Israel time (`resetsAt` 1795533600).
- `burn.json` is fresh: 0 runs, and the next target is Tel Aviv / beauty.
- The `lead-finder` agent type and the `lead-burn` / `find-leads` skills are registered in this session.
- **Not verified yet:** a live scheduled check, whether the push notification reaches the phone, and a full subagent run.
  `decide` has only been tested offline (unit tests, plus a manual run against the real `resetsAt`).

## Known limits and gotchas
- **There's no exact "% left".** "A lot left" means `status == "allowed"` with no overage. A rapid burst of usage
  between the check and the run isn't caught, but the re-check on "go" catches a passed reset.
- **The check itself uses a little usage**, about one short turn per window. A check that fires when no window is active
  starts a new one, which shifts the user's reset times.
- **The chain is fragile.** If a check turn fails before scheduling the next one, the checks stop. `/lead-burn status`
  shows whether one is pending, and `/lead-burn on` restarts the chain. If the session is archived, the checks stop too.
- **`rateLimitType: seven_day`.** When the weekly limit is the binding one, `resetsAt` is the weekly reset, so the
  next check may be days away. That's acceptable: in that case there's no 5-hour leftover worth using.
- **PushNotification** may say "not sent" if the user is at the screen, or if notifications aren't set up. The question is
  always posted in the chat as well.
- The subagent's quality depends on the lead finder's limits: thin OSM data, only the `maps.mail.ru` Overpass mirror
  answering from this cloud, and one WebSearch per lead. See the other handoff.

## Ideas not built yet
1. A **backstop trigger** (daily, recurring) that re-arms the chain if no `lead-burn check` is pending.
2. An email fallback to the user's own inbox (Gmail connector) when the push isn't delivered. Ask the user before building it.
3. Publish each run's phone page as a private artifact instead of only sending the file (this ties into lead-finder idea 1:
   a shared call log).
4. Let the user set the rotation from the chat (`/lead-burn targets haifa,netanya beauty,health`).
5. Scale `verify_count` to the minutes left (for example, about 1 lead per minute).
6. Open a pull request for the branch when the user asks.

## Timeline of this session
1. "Read HANDOFF-lead-finder.md and continue the lead finder. Make it a subagent that uses credits an hour before the reset…"
   The handoff wasn't on this branch, so it was found on `claude/jolly-meitner-s4e01m` and merged in (43 tests passed).
2. Found that `get_session` exposes `rate_limit_info` (the reset time and status, but no percentage). The repo turned out to be public.
3. Built `burn.py`, the CLI, the hashed memory, the subagent, the skill and the tests (51 passing). Updated
   `HANDOFF-lead-finder.md` (section 8) and the README. Committed `b29a31d` ("Add lead-burn…"), pushed, and armed the first check.
4. "Create handoff for this". This file.
