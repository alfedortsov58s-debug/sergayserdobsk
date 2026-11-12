---
name: dewell-quiz-ops
description: >-
  Build, maintain, debug, audit, optimize, back up and safely deploy DEWELL real-estate apartment-selection quizzes (квизы подбора квартир) on REG.RU/ISPmanager shared hosting, including mobile-first cinematics, PHP/MacroCRM leads, price feeds and cron, Yandex Metrika goals, consent and legal pages, recovery and production hotfixes. Use for DEWELL quiz ZIP archives, code/UI defects, CRM delivery or duplicate leads, domain/subdomain migrations, speed fixes, tracking, secure backups and release operations.
---

# DEWELL Quiz Ops

Work from a current hosting export, not an older release or an unverified guess. The user's functioning production code is authoritative. The goal is a minimal, tested patch with a rollback, not a blind redesign.

## Non-negotiables

1. **Inspect before editing.** Unpack a current ZIP safely, inventory all paths, inspect affected selectors/functions and generated data. Never assume earlier ZIPs match production. Compare the current behavior against user screenshots.
2. **Separate concerns.** Keep frontend, price feed, CRM delivery, Metrika, consent/legal, hosting and runtime data distinct. Do not replace PHP/CRM because a mobile layout changed.
3. **No secrets in deliverables.** Never print or distribute actual `private/config.php`, full feed URLs, App_secret, bearer tokens, audit HMAC keys, logs with phones, consent records or server-private ZIPs. Use `scripts/sanitize_snapshot.py` for shareable backups. If a full forensic copy contains secrets, use it only for local analysis; never include those bytes in an output ZIP.
4. **Consent is independent of analytics.** The user must actively check the personal-data consent box before a lead. Analytics/cookie refusal must not block a lead. Do not load Metrika until opted in when promised. Never record the phone in Webvisor.
5. **Server-verified leads only.** Never label HTTP 200 alone as successful. Interpret documented MacroCRM response semantics, including its error fields; do not silently accept arbitrary `{}`. Never mark a refused duplicate as a delivered lead. Retain a unique request ID and consent evidence.
6. **Preserve working behavior.** No invented apartment ID (especially not the cheapest apartment) for an interest-only quiz. No invented client name in the form; use a technical API-only placeholder if required by the provider. Never modify the current price formula without explicit business rules.
7. **No production access assumptions.** The user operates ISPmanager Shell. Return one *single-line* command per step, always prefixed by `cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && ...` when working on this site. Avoid multiline heredocs pasted into browser Shell; the panel concatenates lines. Ask for the result of the one command before moving on when interacting with the live server.
8. **Keep backups and rollback.** Before replacing a file, back it up outside public web paths or in a strictly denied private directory. Supply only changed files in ZIP patches, with clear destination and exact content list. No installation wizard or secret files in public releases.

## Workflow

1. **Brief/state:** Confirm which project/domain and the latest export. Record actual file hashes, active versions and last verified behavior. Use `references/project-contract.md` for ПРОСТОР and WELLARTCITY patterns.
2. **Inventory/security:** Run `scripts/audit_snapshot.py` on the ZIP or unpacked tree; inspect `.htaccess`, public exposure of `private/`, `cron/`, `setup.php`, runtime logs, sensitive configs and temporary ZIPs. Do not echo secret values.
3. **Change:** Make the smallest justified source edit. For mobile crop, inspect the actual underlying image and selectors; test 320×568, 375×667, 390×720, 390×844 and 430×932. Keep legal pricing note visible at the bottom as requested for ПРОСТОР. Never hide mandatory text to solve layout by accident.
4. **Integrations:** Check existing MacroCRM payload builder, real request/response examples and current project-approved contract in `references/project-contract.md`. For site-based API 1.0 sign with the **correct domain and secret**; reuse working WELLARTCITY request conventions where supported, not a made-up API 2.0 switch. Verify successful CRM record and actual visible comment.
5. **Tracking:** Preserve Metrika counter `104593957` and IDs `start`, `question1`, `question2`, `question3`, `send` for ПРОСТОР. Goals must not fire before analytics consent; `send` only after confirmed lead. Do not add question4/5 goals unless approved; keep historical comparability.
6. **Price:** Keep MacroCRM feed URL only in private config. Cron every 30 min; reject invalid numbers; write `data/price.json` atomically. Show an honest price note with price, apartment number, section and last successful check date; hide stale price after 90 min. Preserve price/availability source distinctions.
7. **QA:** Validate PHP via `php -l`, parse inline JavaScript with Node, verify assets and responsive screenshots, confirm consent/CRM branches locally with mocked responses. Test frontend on Chromium plus Safari/mobile where possible. Do not fake a live CRM send as a successful test.
8. **Release/restore:** Package only touched public files for hotfixes. For safe full public snapshots use `scripts/sanitize_snapshot.py` with a current hosting ZIP. Follow `references/hosting-and-security.md` and `references/qa-and-release.md`. Verify archive contents and hashes before linking.

## Output standard

Provide: (a) succinct diagnosed cause with evidence, (b) exact files changed, (c) runnable ZIP or one-line Shell operation, (d) rollback and verification, (e) what was *not* tested (real iPhone/CRM/hosting). Do not imply production was modified unless the user ran the command or a connected action confirmed it.

## References

- `references/project-contract.md` — current ПРОСТОР project, quiz screens, CRM, price and Metrika contract.
- `references/hosting-and-security.md` — REG.RU/ISPmanager layout, secure backups, setup closure, single-command Shell usage.
- `references/qa-and-release.md` — safe checks and deployment gates.
- `scripts/sanitize_snapshot.py` — sanitized shareable ZIP from a private hosting ZIP.
- `scripts/audit_snapshot.py` — structural and secret-risk audit without printing values.
