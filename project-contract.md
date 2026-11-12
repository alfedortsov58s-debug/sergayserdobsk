# ПРОСТОР — verified quiz project contract (12 November 2026)

## Environment

- Live host: `https://quiz.dewell-prostor.ru/` under REG.RU ISPmanager, account `u3713387`, site root `/var/www/u3713387/data/www/quiz.dewell-prostor.ru`.
- Main `dewell-prostor.ru` runs separately on Tilda: DO NOT alter its DNS or files to fix the quiz.
- Static HTML/CSS/JS frontend (`index.html`), optimized images (`assets/scenes/*.desktop.*.webp` and `*.mobile.*.webp`), `api/lead.php`, `cron/update-price.php`, `data/price.json`, legal pages and denied `private/`.
- Functional code has accumulated v11→v23 hotfixes; `release.json` in the 16:58 export still said v11. Determine state from actual files, not that label alone.
- The initialization `setup.php` was moved to `private/setup.php.disabled` on 12 November 2026; public `/setup.php` was confirmed inaccessible by the user. Keep it out of any release and shared backup.

## User journey

- Hero: title, description, benefits, button “Начать подбор квартиры”, visible architecture; **price note and legally necessary developer information must be visible at the bottom of the first screen on mobile** (specific latest requirement). Road/asphalt should not dominate the picture; inspect mobile WebP crop and actual CSS, not generic `background-position` guesses.
- Q1: room count (1 / 2 / 3 / undecided).
- Q2: floor range (1–2 / 3–5 / 6–8 / unimportant).
- Q3: finish (prefinish / turnkey / compare).
- Q4: living priorities; multi-selection of six features (courtyard, children's areas, sports, panoramas, low/mid-rise 5–8 floors, schools etc., verify exact current UI copy).
- Q5: payment (mortgage, installment, cash, trade-in, exploring).
- Final: phone + unchecked personal data consent + explicit policy/consent links. No name input. Success view should **not** reveal Request ID to client, but ID must remain in CRM and internal evidence.
- Avoid heavy hero files embedded as Base64: separate responsive WebP; first screen first, next screen prefetch as needed.

## MacroCRM / lead

- Working reference implementation: WELLARTCITY `ajax/send.php` (available as user-provided source in conversation), MacroCRM API 1.0 `/estate/request/`.
- For v1 sign `md5(domain . timestamp . site_app_secret)` from server-side config; do not expose signing key or URL feed tokens.
- Send JSON as in known-good WELLARTCITY, including `domain`, `time`, `token`, `action=buy`, technical `name` if needed by provider, `phone`, human-readable `message`, `request_id`, `is_allow_personal_data`, channel, UTM and `yclid` where captured and permitted.
- Comment: brief preference summary, 5 actual answers, ЖК «ПРОСТОР» **without inventing a selected apartment**, MARKETING, TECHNICAL DATA, CONSENT status and version. Bind to a house ID only if the real MacroCRM ID and schema are verified.
- Failed examples: `HTTP 200` with `{error, message}` and text “Нам нужно знать как к вам обращаться” or “Отклонено повторное обращение”. A user confirmed a real accepted lead after using the v19-style WELLARTCITY request approach; do not assume duplicate behavior without retesting against real CRM settings.
- **Important:** One audited historical backend success checker treated arbitrary `{}` as success; do not copy this. A future fix needs to use the real provider success response and estate identifier according to captured response; protect backward compatibility.

## Price and legal

- Feed in `private/config.php` (secret URL); `cron/update-price.php` every `*/30 * * * *`; latest public data `data/price.json`. Ignore zero/invalid prices and protect a last known-good response.
- Price note: “Цена N ₽ указана для квартиры № X, секция Y, по состоянию на DD.MM.YYYY и при наличии объекта в продаже.” No MacroCRM brand mention in user-facing pricing text. Display stale/unavailable state honestly.
- Site/developer: ООО СЗ «НОВАЯ СРЕДА»; first lead personal data operator: ИП Курносов С. А. Respect current published documents `legal/privacy.html`, `legal/consent.html`, `legal/cookies.html`, `legal/terms.html`, consent version and legal disclaimer; do not blindly port legal text between projects.

## Yandex Metrika

- Existing counter `104593957` from the former quiz. Keep historical goal IDs/identifiers unchanged:
  - `start` / 473829781 — begin quiz
  - `question1` / 473829802 — open Q1
  - `question2` / 473829873 — open Q2
  - `question3` / 473829892 — open Q3
  - `send` / 473829899 — CRM-confirmed lead
- Actual UI has five questions; do not add historical goal IDs for Q4/Q5 without approval.
- Frontend tracking source `assets/quiz-metrika.v21.js`. Run only after analytics-cookie opt-in; refuse = zero tracking requests/goals; queue pre-consent goals only in volatile memory, flush after opt-in, dedupe navigations; `send` after server success. Do not enable Webvisor phone capture.
