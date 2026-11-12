# REG.RU / ISPmanager quiz hosting and safe archives

## Default directory map

`/var/www/u3713387/data/www/quiz.dewell-prostor.ru/` has `index.html`, `assets/`, `api/`, `cron/`, `data/`, `legal/`, `private/`, `.htaccess`, `robots.txt`, `release.json`. `private/` carries production `config.php`, backups, logs and consent evidence; `cron/` contains update-price PHP but must not be browsable.

## Security rules

- `private/.htaccess` and `cron/.htaccess`: `Require all denied`; root rewrite also forbids those folders. On 12 Nov 2026 the user verified `GET/HEAD private/runtime/consents.jsonl` yielded HTTP `403`.
- Exposed `setup.php` previously responded `200`; user moved it to `private/setup.php.disabled` and confirmed problem closed. Future snapshots must omit setup/installers even if they were present in old exports.
- Avoid copies of `private/config.php` in public ZIP, public `.bak`/logs, and `api/` debug scripts. A publicly downloadable full hosting ZIP contains passwords, phone numbers and consent logs; remove it from `/www/` after backup.
- Restrict sensitive files to owner (`chmod 600` files where PHP deployment permits), private runtime dirs `700`; verify web runtime can still write.
- Store backups outside web root; for a full disaster-recovery backup of private state, encrypt before transfer to a durable location. A sanitized public backup is **not** a sufficient replacement for private config/consent evidence.
- Change/revoke already disclosed app secrets or signed export URLs when practical.

## Safe sanitized ZIP

`python3 scripts/sanitize_snapshot.py SOURCE.zip OUTPUT.zip`.

Whitelists known public application file types and approved endpoints; drops `private/config.php`, private backups, runtime logs, `setup.php`, temp ZIPs and history. Contains `site/` tree, a harmless `private/config.example.php`, `RESTORE.md`, `MANIFEST.json` and checksums. It is **not** a direct full-server restoration or a backup of actual secrets.

## Browser Shell UX

The user's ISPmanager browser shell frequently collapses pasted newlines, resulting in stuck `>` prompts, bash history expansion `!` errors and accidental concatenation of commands. Every Shell instruction should be **a single-line command**, beginning with:

`cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && ...`

If `>` appears, press Ctrl+C. Never paste heredoc or multiple unrelated commands there. Give exactly one command per turn during live diagnostics, ask for its result before next command.

## Typical checks (one at a time)

- PHP parse: `cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && php -l api/lead.php`
- Price cron: `cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && php cron/update-price.php`
- Private access: `cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && curl -sS -I -o /dev/null -w 'HTTP %{http_code}\n' https://quiz.dewell-prostor.ru/private/runtime/consents.jsonl`
- Installed setup: `cd /var/www/u3713387/data/www/quiz.dewell-prostor.ru && curl -sS -I -o /dev/null -w 'HTTP %{http_code}\n' https://quiz.dewell-prostor.ru/setup.php` (expect 404).

Never ask for full private config or full CRM response body as a chat message. Use safe field/status summaries; redact sensitive fields from logs.
