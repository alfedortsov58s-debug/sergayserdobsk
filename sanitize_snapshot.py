#!/usr/bin/env python3
"""Create a non-secret shareable public backup from a REG.RU hosting ZIP.

Only explicitly allowed project files are copied. No config.php, live logs,
consent journal, exposed setup installer, private archives or secrets.
Usage: python3 sanitize_snapshot.py server-export.zip safe-public-backup.zip
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


_ALLOWED_FILES = {
    ".htaccess", "index.html", "robots.txt", "release.json",
    "api/lead.php", "cron/update-price.php", "cron/.htaccess",
    "data/.htaccess", "data/price.json", "private/.htaccess",
}
_ALLOWED_ASSET_SUFFIXES = {".js", ".css", ".webp", ".avif", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff2"}
_SAFE_CONFIG_EXAMPLE = """<?php
// Example only. Configure locally on the server. NEVER publish production secrets.
return [
    'feed_url' => '', // signed/export URL: treat as secret
    'macro_api_version' => 'v1',
    'macro_url' => 'https://api.macroserver.ru/estate/request/',
    'macro_site_domain' => 'quiz.dewell-prostor.ru',
    'macro_app_secret' => '',
    'audit_hmac_key' => '',
];
"""


def _check_path(path: str) -> None:
    if path.startswith("/") or "\\" in path or "\x00" in path or any(x in ("..", ".") for x in path.split("/")):
        raise ValueError("Unsafe archive member path")


def _source_prefix(names: list[str]) -> str:
    opts = [n[: -len("index.html")] for n in names if n.endswith("index.html")]
    # Take the shortest path containing the root index, not a nested sample.
    if not opts:
        raise ValueError("No root index.html found")
    return min(opts, key=len)


def _allowed(rel: str) -> bool:
    if rel in _ALLOWED_FILES:
        return True
    if rel.startswith("assets/") and len(rel.split("/")) >= 2:
        return (rel == "assets/scenes/.htaccess" or Path(rel).suffix.lower() in _ALLOWED_ASSET_SUFFIXES)
    if rel.startswith("legal/") and rel.count("/") == 1:
        return rel.endswith(".html")
    return False


def _extract_secret_literals(config_source: bytes) -> list[bytes]:
    # Do not print anything extracted here. Detect any accidental embedding in public files.
    text = config_source.decode("utf-8", "replace")
    out: list[bytes] = []
    for key in ("feed_url", "macro_app_secret", "macro_token", "audit_hmac_key"):
        rx = rf"['\"]{re.escape(key)}['\"]\s*=>\s*(['\"])(.*?)\1"
        for m in re.finditer(rx, text):
            raw = m.group(2)
            if len(raw) >= 12:
                out.append(raw.encode("utf-8"))
    return out


def main(input_path: Path, output_path: Path) -> None:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must differ")
    result: dict[str, bytes] = {}
    with zipfile.ZipFile(input_path) as source:
        names = [i.filename for i in source.infolist()]
        for info in source.infolist():
            _check_path(info.filename.rstrip("/"))
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Symlink in input archive not supported")
        prefix = _source_prefix(names)
        config_path = prefix + "private/config.php"
        secret_literals = _extract_secret_literals(source.read(config_path)) if config_path in names else []
        for name in names:
            if not name.startswith(prefix):
                continue
            rel = name[len(prefix):]
            if not rel or name.endswith("/") or not _allowed(rel):
                continue
            # Always replace stale release metadata with truthful backup-specific metadata.
            if rel == "release.json":
                continue
            data = source.read(name)
            for secret in secret_literals:
                if secret in data:
                    raise ValueError("Secret-like configuration value occurs in an allowed public file; review manually")
            result["site/" + rel] = data
    required = ["site/index.html", "site/api/lead.php", "site/cron/update-price.php", "site/private/.htaccess", "site/.htaccess", "site/assets/quiz-metrika.v21.js"]
    missing = [x for x in required if x not in result]
    if missing:
        raise ValueError("Missing expected public files: " + ", ".join(missing))

    # No installer (setup.php) and no actual production secrets or identifiable journals.
    result["site/private/config.example.php"] = _SAFE_CONFIG_EXAMPLE.encode("utf-8")
    result["site/release.json"] = (json.dumps({
        "site": "quiz.dewell-prostor.ru",
        "version": "safe-public-snapshot-v23-2026-11-12",
        "entry": "index.html",
        "snapshot_source": "hosting export 2026-11-12 16:58 MSK; setup.php excluded after operator-confirmed shutdown",
        "installer": None,
        "excludes": ["private/config.php", "private/runtime", "private/installed.lock", "setup.php", "server backups"],
        "status": "public backup only; private server config must be restored separately",
    }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    restore = """# DEWELL / ПРОСТОР — безопасная копия публичной части

Этот ZIP создан на основе выгрузки `quiz.dewell-prostor.ru` от 12.11.2026, 16:58 МСК с учётом подтверждённого позднее закрытия `setup.php`. В папке `site/` находится публичная часть сайта с WebP-изображениями, PHP-обработчиком заявок, Cron, юридическими документами и файлом цены.

## Безопасность и ограничения

- В архиве **нет** рабочего `private/config.php`, настоящего `App_secret`, `audit_hmac_key`, подписанной ссылки ценового фида, клиентских телефонов, журналов обращений/согласий и любых бэкапов конфигурации.
- `site/private/config.example.php` — НЕ готовая конфигурация. Она не содержит действующих ключей. Не подменять ей рабочий `private/config.php`.
- `site/release.json` заново создан специально для этого бэкапа; оригинальный `release.json` исходной выгрузки устарел и содержал v11.
- В архиве нет `setup.php`: ранее публичный мастер установки был перемещён в защищённую папку и отключён.
- Это копия *публичного приложения*. Для восстановления на новом сервере требуется **отдельно** восстановить закрытую конфигурацию и журнал согласий из защищённого локального/зашифрованного хранилища.

## Восстановление

1. Выключить приём новых заявок или использовать временный тестовый домен, сохранить действующую папку сайта.
2. Распаковать архив на компьютер. Загрузить **содержимое папки `site/`** в `/var/www/u3713387/data/www/quiz.dewell-prostor.ru/`, не вложенную папку `site`.
3. Восстановить действующий `private/config.php` из отдельной защищённой копии. Если нет ключей — запросить новые у администраторов MacroCRM/фида. НИКОГДА не заполнять ключи в браузерном HTML или в чат.
4. Проверить запрет HTTP-доступа к `private/` и `cron/` (ответ 403/404), а также отсутствие `/setup.php` (404).
5. Выполнить `php -l api/lead.php`, `php -l cron/update-price.php`, вручную запустить скрипт цены и проверить `data/price.json`. Вернуть Cron `*/30 * * * *` на актуальный PHP.
6. Проверить первый экран на смартфоне, пять шагов квиза, юридические ссылки, согласие, отправку одной реальной тестовой заявки и достижение `send` в Метрике только после успеха CRM.
7. Удалить с web-root архивы/бэкапы и убедиться, что они не доступны публично.

## Рекомендация для полноценной аварийной копии

Создать **отдельную зашифрованную** резервную копию `private/config.php`, журналов согласия/CRM и нужных серверных настроек. Хранить *вне* `/www/` с ограниченными правами. Запрещено передавать нешифрованную приватную копию через публичную ссылку.
"""
    result["RESTORE.md"] = restore.encode("utf-8")

    hashes = {k: hashlib.sha256(v).hexdigest() for k, v in sorted(result.items()) if k.startswith("site/")}
    result["SHA256SUMS.txt"] = ("\n".join(f"{hashes[n]}  {n}" for n in sorted(hashes)) + "\n").encode()
    result["MANIFEST.json"] = (json.dumps({
        "backup_type": "sanitized-public-site",
        "site": "quiz.dewell-prostor.ru",
        "source_export": input_path.name,
        "source_export_as_of": "2026-11-12 16:58 MSK",
        "known_post_export_action": "setup.php disabled and moved to private/setup.php.disabled",
        "secret_files_included": False,
        "public_files": len(hashes),
        "total_site_file_bytes": sum(len(v) for k,v in result.items() if k.startswith("site/")),
        "sha256": hashes,
    }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=8) as out:
        for name, value in sorted(result.items()):
            out.writestr(name, value)
    with zipfile.ZipFile(output_path) as created:
        if created.testzip() is not None:
            raise ValueError("ZIP failed CRC validation")
    print(f"OK: public backup created, {len(hashes)} app files, {output_path.stat().st_size} bytes")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: sanitize_snapshot.py server-export.zip safe-public-backup.zip")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
