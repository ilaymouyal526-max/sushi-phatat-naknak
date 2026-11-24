---
name: lead-burn
description: Use leftover Claude plan usage before it resets by running a lead-finder subagent (website-lead-finder, or app-lead-finder once the app profile exists) in the last hour of the usage window, but only after notifying the user and getting a "go". Use for "/lead-burn check" (fired by the scheduled check), "/lead-burn go [app] [city] [category] [count]" or a plain "go"/"go app"/"yes" reply to a burn notification, "/lead-burn skip", "/lead-burn status", "/lead-burn on|off", "/lead-burn set …", or "use my leftover credits for leads".
---

# /lead-burn: spend leftover usage on leads, with permission

The plan's usage window resets on a schedule. Usage left at the reset is lost, so about **70 minutes before each reset**
a scheduled check looks at the window. If usage is plentiful it **notifies the user and asks**. Only on a "go" does it run
a lead-finder subagent until 5 minutes before the reset:
- **`website-lead-finder`** (`.claude/agents/website-lead-finder.md`): the default. Businesses that need a quick website.
- **`app-lead-finder`** (`.claude/agents/app-lead-finder.md`): only on `go app …`, and only when the app profile is ready
  (`burn status` → `app_profile.ready`). The profile comes from a handoff file the user is waiting for from a friend.
The notification comes first, so the user can keep the usage for another project instead.

CLAUDE.md applies: running the subagent spends usage, so **no run without an explicit "go" for that window**.
No answer means no run. A "go" covers one run in one window only.

State: `lead_agent/state/burn.json` (committed; settings, rotation, run counts, hashed ids, **no lead data**).
Engine: `python3 -m lead_agent burn decide|asked|target|finish|status|set`.

## Reading the usage window
Call `get_session` (claude-code-remote) with no `session_id`. Use `external_metadata.rate_limit_info`:
- `resetsAt`: when the current window resets (epoch seconds)
- `status`: `allowed` (plenty left), or `allowed_warning` / `rejected` (little or none left)
- `isUsingOverage`, `rateLimitType` (`five_hour` usually; `seven_day` when the weekly limit is the one that's close)
There is no exact percentage. **"A lot left" means `status` is `allowed` with no overage.** Be honest about this if asked.

## Scheduling (one pending check at a time)
Checks are one-shot `send_later` messages into this session, named **`lead-burn check`**, with the message
`/lead-burn check`. Every check schedules the next one. Before scheduling, run `list_triggers` and
`delete_trigger` any other pending `lead-burn check`, so there is never more than one.
Schedule with `at` = the `next_check` epoch as an RFC3339 UTC time (`date -u -d @<epoch> +%FT%TZ`) and
`initiation: "human_request"` (the user asked for this automation on 2026-11-24).

## `/lead-burn check` (fired by the schedule; the user is probably away)
1. Read the window (above), then run
   `python3 -m lead_agent burn decide --resets-at <resetsAt> --status <status> [--overage]`.
2. By `action`:
   - `off`: schedule nothing. Say "lead-burn is off" in one line.
   - `wait` / `skip`: schedule the next check at `next_check`. Reply with one short line (reason + next check time).
     **No push notification.**
   - `notify`:
     a. `python3 -m lead_agent burn asked <resets_at>`.
     b. **PushNotification** (one line, under 200 chars), e.g.
        `Claude usage resets 17:20 with plenty left. Reply "go" for website leads (Tel Aviv beauty, 40) till 17:15, or ignore to keep it.`
        Only if `app_profile.ready` is true (from `burn status`), add ` "go app" = app leads.` (keep it under 200 chars).
     c. Post the same question in the chat with the options: `go`, `go <city> <category> <count>`,
        `go app [city] [count]` (only if the app profile is ready), `skip`.
     d. Schedule the next check at `next_check`. End the turn and **wait**. Don't start anything.
3. Commit `lead_agent/state/burn.json` if it changed (`git add lead_agent/state/burn.json`, message
   "lead-burn: update state"), and push to the session's branch.

## "go" / "go app" (the user's reply to a notification, or `/lead-burn go …`)
1. Re-read the window. If the reset has already passed or fewer than 25 minutes remain, say so and don't run.
   If `/lead-burn go` comes with no recent notification, it's still a valid request: use the current window's reset.
2. Focus: `app` if the reply says "app", otherwise `website`. For `app`, check `burn status` → `app_profile.ready`.
   If it's not ready, say the app profile is still waiting on the friend's handoff and offer `go` (website) instead. Don't run.
3. Target: the user's city/category/count if given. Otherwise use `python3 -m lead_agent burn target` and `verify_count`
   from `burn status`. For `app`, use the rotation's city with no category (the agent uses the profile's categories).
   Deadline = reset − 5 min, in Israel time.
4. Start the subagent: **`website-lead-finder`** or **`app-lead-finder`** (Agent tool with that `subagent_type`). If that
   type isn't listed, use `general-purpose` and tell it to read and follow `.claude/agents/<name>.md`. Pass city,
   category, verify_count and deadline. Run it in the foreground so the files exist when it returns.
5. When it returns:
   - `python3 -m lead_agent burn finish --run <run.json> --resets-at <resetsAt> --focus <website|app>`
     (add `--city … --category … --no-advance` if the user picked a custom target).
   - Send the `.html` phone page and the `.xlsx` to the user with **SendUserFile** (status `proactive`). The container's
     `leads/` folder doesn't survive restarts, so this is how the user keeps them.
   - PushNotification: `Website leads done: <N> Hot, <M> Warm in <city> <category>. Phone page + sheet in the chat.`
     (for app runs: `App leads done: <N> high fit, <M> medium in <city>. …`)
   - In the chat: the subagent's top-10 table, stats, the compliance line from `/find-leads`, and the next target.
   - Commit and push `lead_agent/state/burn.json` only. **Never commit `leads/`.**

## Other commands
- `skip` (reply to a notification): say OK and do nothing. The next check is already scheduled.
- `/lead-burn status`: `python3 -m lead_agent burn status` (includes whether the app profile is ready), the current
  window (reset time, status), and the pending `lead-burn check` from `list_triggers`.
- `/lead-burn off`: `burn set --enabled off`, then delete every pending `lead-burn check`.
- `/lead-burn on`: `burn set --enabled on`, then run a check now (same steps as `check`).
- `/lead-burn set --verify-count N | --notify-before MIN | --quiet HH:MM-HH:MM`: pass through to `burn set`.

## Defaults (change with `set`)
Ask 70 min before the reset; the run stops 5 min before it; no question if under 25 min are left; quiet hours
23:00–08:00 Israel time (no notifications, that window is skipped); 40 leads verified per run; website runs
rotate through 16 cities × beauty, health, trades, auto, fitness, professional. Website and app runs remember
delivered leads separately, so one business can be offered both; a "not interested" blocks it for both. Leads delivered by earlier burn runs, and
businesses that said no, are skipped even after the container is reset (hashed ids in the state file).

## Limits to tell the user about
- Only the current window's reset is visible, not an exact amount left. `allowed` = no limit warning yet.
- The check itself is a short turn, so it uses a little usage (about one check per 5-hour window).
  A check that runs when no window is active starts a new window.
- If the session is archived or deleted, the checks stop. Run `/lead-burn on` in a new session to restart them.
- Push notifications reach the phone only when the Claude app is set to receive them. The question is always
  in the chat too.
