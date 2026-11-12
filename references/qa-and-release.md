# Quiz QA and release gate

## Inventory and dependencies

1. Inventory current archive using `scripts/audit_snapshot.py`, inspect version claims and identify the latest deployed `index.html`, `api/lead.php`, `assets/quiz-metrika.v21.js`.
2. Review public resources in HTML. Ensure image/JS/CSS paths exist, MIME matches and cache policy doesn't prevent instant updates.
3. Confirm `private/config.php`, consent records, logs and API/feed keys are absent from any release ZIP. Check ZIP for paths escaping root and symlinks.
4. Confirm `setup.php` is absent, and private/cron HTTP requests return 403/404.

## Visual and functional

- Inspect source WebP and CSS focal point. Check hero and legal block on 320×568, 375×667, 390×600, 390×720, 390×844, 430×932, desktop 1024 and 1440 widths. Do not call it fixed until screenshot composition is acceptable.
- All five Q steps accessible, progress/back functional; selected values preserved. No outgoing/duplicate screen overlay. No mobile horizontal scroll or hidden CTA.
- Test cookie banner under short height. Verify personal-data consent checkbox begins unchecked, legal links open and required consent is enforced on server.
- Price heading, note, `price.json` timestamp and stale-state all correct.
- Test success/error branch of form locally against mocked server; don't actually submit private user data in QA.

## Integration

- MacroCRM v1 JSON signing; test `phone` and answer values, valid consent, `is_allow_personal_data`, UTM, request_id, correct domain, technical name only in request payload. Preserve submitted answer labels as seen in UI.
- Success confirmed by actual provider marker, not HTTP 200 alone; record `request_id` and sanitized outcome. Duplicate errors not silently treated as success.
- Metrika 104593957: no `mc.yandex.ru` before consent; `start`, `question1`, `question2`, `question3`, `send` map to historic events; denied cookies yields no reachGoal; accepted yields no duplicate goals; `send` fires only on successful CRM response.
- Cron manual run and next scheduled run both update `checked_at`; min price matches eligible feed data and no stale/wrong promotions.

## Packaging

- For simple style patch, release only `index.html`. For lead patch, only `api/lead.php`. Do not replace existing private config, images or cron unrelated to the fix.
- Validate `php -l`; for scripts run `node --check`. Perform browser responsive screenshots where supported.
- Make backup of replaced production files. If migration changes paths, write explicit upgrade and rollback; defer risky restructuring to separate version.
- In final answer state verified vs unverified (actual ISPmanager/real iPhone/live CRM), the exact ZIP paths, and minimal installation steps.
