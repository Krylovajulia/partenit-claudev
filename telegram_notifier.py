"""Telegram notifications for Trust Layer Pipeline."""
import logging
import os

import httpx

logger = logging.getLogger("pipeline.telegram")

_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
_BASE = "https://api.telegram.org"


def _send(text: str) -> None:
    if not _TOKEN or not _CHAT_ID:
        return
    try:
        httpx.post(
            f"{_BASE}/bot{_TOKEN}/sendMessage",
            json={"chat_id": _CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=5,
        )
    except Exception as e:
        logger.warning("Telegram send failed: %s", e)


def notify_pipeline_started(parent_key: str, summary: str, jira_domain: str) -> None:
    url = f"https://{jira_domain}/browse/{parent_key}"
    _send(
        f"🚦 <b>Пайплайн запущен</b>\n"
        f"Задача: <a href='{url}'>{parent_key}</a>\n"
        f"{summary}"
    )


def notify_subtasks_created(parent_key: str, subtask_keys: list[str],
                             labels: list[str], jira_domain: str) -> None:
    url = f"https://{jira_domain}/browse/{parent_key}"
    keys_str = " · ".join(subtask_keys)
    labels_str = " ".join(f"#{l}" for l in labels) if labels else "—"
    _send(
        f"📋 <b>Подзадачи созданы</b>\n"
        f"Задача: <a href='{url}'>{parent_key}</a>\n"
        f"Подзадачи: {keys_str}\n"
        f"Лейблы: {labels_str}"
    )


def notify_stage_started(stage: str, issue_key: str, parent_key: str,
                          jira_domain: str) -> None:
    emoji = {"sys-analysis": "📊", "architecture": "🏗",
             "development": "💻", "testing": "🧪"}.get(stage, "⚙️")
    name = {"sys-analysis": "Системный анализ", "architecture": "Архитектура",
            "development": "Разработка", "testing": "Тестирование"}.get(stage, stage)
    url = f"https://{jira_domain}/browse/{issue_key}"
    _send(
        f"{emoji} <b>{name} — начат</b>\n"
        f"Задача: <a href='https://{jira_domain}/browse/{parent_key}'>{parent_key}</a>\n"
        f"Подзадача: <a href='{url}'>{issue_key}</a>\n"
        f"Claude Code работает..."
    )


def notify_artifact_done(stage: str, issue_key: str, parent_key: str,
                         jira_domain: str, duration_s: int) -> None:
    emoji = "📊" if stage == "sys-analysis" else "🏗"
    title = "Системный анализ" if stage == "sys-analysis" else "Архитектурное решение"
    url = f"https://{jira_domain}/browse/{issue_key}"
    _send(
        f"{emoji} <b>{title} готов</b>\n"
        f"Задача: <a href='https://{jira_domain}/browse/{parent_key}'>{parent_key}</a>\n"
        f"Подзадача: <a href='{url}'>{issue_key}</a>\n"
        f"⏱ {duration_s // 60}м {duration_s % 60}с"
    )


def notify_pr_created(issue_key: str, parent_key: str, pr_url: str,
                      jira_domain: str, files_count: int) -> None:
    _send(
        f"🔀 <b>PR создан</b>\n"
        f"Задача: <a href='https://{jira_domain}/browse/{parent_key}'>{parent_key}</a>\n"
        f"<a href='{pr_url}'>Открыть PR</a> · {files_count} файлов"
    )


def notify_testing_done(issue_key: str, parent_key: str,
                        jira_domain: str, duration_s: int) -> None:
    url = f"https://{jira_domain}/browse/{issue_key}"
    _send(
        f"🧪 <b>Тесты написаны</b>\n"
        f"Задача: <a href='https://{jira_domain}/browse/{parent_key}'>{parent_key}</a>\n"
        f"Подзадача: <a href='{url}'>{issue_key}</a>\n"
        f"⏱ {duration_s // 60}м {duration_s % 60}с"
    )


def notify_all_done(parent_key: str, jira_domain: str) -> None:
    _send(
        f"✅ <b>Готово к ревью!</b>\n"
        f"<a href='https://{jira_domain}/browse/{parent_key}'>{parent_key}</a>\n"
        f"Все этапы завершены: анализ → архитектура → код → тесты\n"
        f"Посмотри PR и двигай задачу в <b>Ready to Merge</b>"
    )


def notify_merged(issue_key: str, pr_url: str, base_branch: str,
                  jira_domain: str) -> None:
    url = f"https://{jira_domain}/browse/{issue_key}"
    _send(
        f"🚀 <b>Смерджено в {base_branch}!</b>\n"
        f"Задача: <a href='{url}'>{issue_key}</a>\n"
        f"<a href='{pr_url}'>PR</a> → Done"
    )


def notify_error(issue_key: str, stage: str, error: str, jira_domain: str) -> None:
    url = f"https://{jira_domain}/browse/{issue_key}"
    _send(
        f"❌ <b>Ошибка пайплайна</b>\n"
        f"Этап: {stage}\n"
        f"Задача: <a href='{url}'>{issue_key}</a>\n"
        f"<code>{error[:200]}</code>"
    )
