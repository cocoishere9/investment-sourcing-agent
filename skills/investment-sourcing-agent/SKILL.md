---
name: investment-sourcing-agent
description: Run an AI and technology investment sourcing subagent workflow in Codex: fetch public signals, score them, update a master XLSX, write daily Markdown reports, draft bilingual outreach, and send selected Gmail messages only after confirmation.
---

# Investment Sourcing Agent

Use this skill when the user asks to run, inspect, design, or operate the investment sourcing workflow for AI, AI hardware, robotics, AI infrastructure, agent infrastructure, inference, scientific AI, GitHub projects, arXiv papers, YC companies, HN launches, founder discovery, or outreach.

This skill is the user-facing entrypoint. Do not tell the user to operate a CLI. You may use local deterministic modules, scripts, or connectors underneath, but Codex and this skill are the operating surface.

## Load Order

Before acting, read the subagent manual:

`agents/investment-sourcing-agent/AGENTS.md`

If the file is missing, continue with this skill's rules and tell the user that the subagent manual is missing.

## Core Contract

- Codex is the operating console.
- The first version is manual or manually triggered. Do not create a recurring automation unless the user explicitly asks later.
- Keep the workflow modular. Each stage can run alone or as part of `daily_run`.
- Use real public data only. Never fabricate missing source data.
- Fetch at most 20 items per source by default.
- Maintain one long-lived master XLSX table.
- Write Top daily details into a date-specific Markdown report.
- Draft both English and Chinese outreach emails.
- Gmail sending requires numbered user selection plus a second explicit confirmation.

## Standard Actions

Map natural-language requests to these actions.

### `daily_run`

Run the full first-version workflow:

1. Fetch configured sources.
2. Process items by artifact type.
3. Score items with type-specific rubrics.
4. Update the master XLSX.
5. Render the daily Markdown report with Top 10-15 entries.
6. Draft outreach for eligible candidates.
7. Show the Top summary and any outreach candidates in Codex.

### `fetch_only`

Fetch source data without scoring or outreach. Use when the user asks to refresh sources, inspect source health, or run only a subset such as GitHub and arXiv.

### `process_only`

Transform fetched raw items into typed signals: company, repo, paper, or post.

### `score_only`

Score or rescore processed items using the current taste and rubric rules.

### `show_digest`

Show the current day's Top 10-15 in Codex and link to the Markdown report.

### `draft_outreach`

Generate bilingual outreach drafts for candidates that meet the outreach rule: high enough type-specific score or tier plus a public email or clear contact path.

### `review_outreach`

Show numbered pending outreach candidates. For each candidate, include recipient, source item, why it was selected, English subject/body, Chinese subject/body, and evidence links.

### `send_selected`

When the user says something like "发送 1、3、5":

1. Repeat the exact selected recipients and subjects.
2. Ask for final confirmation.
3. If the user confirms, use Gmail tools to send.
4. Record send status and message/thread IDs when available.

Do not send after selection alone.

### `backfill_date`

Rerun or repair a specific date. Preserve existing rows and update `last_seen_date`, status, score, evidence, and report anchors as needed.

### `rescore_master`

Use updated taste or rubric rules to rescore historical master table rows.

## Source Defaults

Stable first-version sources:

- YC Startup Directory or documented public fallback.
- GitHub public repositories.
- arXiv public API.
- Hacker News official Firebase API.
- Algolia HN Search when keyword search is needed.
- Webpage or RSS only when configured.

Treat YC as semi-stable because YC does not provide an official public API. Prefer documented public endpoints or page parsing with clear failure reporting.

## Taste Priorities

Preferred themes:

- AI infra, DevTools, and agent infrastructure.
- Inference, AI hardware, and edge AI.
- Robotics.
- Scientific AI.
- 华人/中国背景 founder recall.
- Cross-border China or global opportunities.

Founder, author, and maintainer background is especially important. Look for elite technical universities, core labs, major research groups, top conference work, strong open-source history, AI infra or robotics experience, and founder-like shipping behavior. Treat this as a strong additive signal, not a hard filter.

## Type-Specific Rubrics

Use 0-100 scores within each artifact type.

### Company

- Founder background: 35
- Theme fit: 20
- Technical asset or product depth: 20
- Product clarity or traction: 15
- Contactability: 10

### Repo

- Maintainer background: 25
- Technical depth: 25
- Adoption or momentum: 20
- Theme fit: 15
- Commercialization and contactability: 15

### Paper

- Author or lab background: 30
- Novelty and technical relevance: 25
- Implementation or commercialization path: 20
- Theme fit: 15
- Contactability or project link: 10

### Post

- Traceable entity quality: 30
- Technical or product detail: 25
- Founder or background clue: 20
- Engagement and freshness: 15
- Theme fit and contactability: 10

## Negative Signals

Apply meaningful penalties or mark as not outreach-ready for:

- Pure AI wrapper.
- No technical artifact.
- No public contact path.
- Too late stage.
- Funding news without product detail.
- Obvious big-company internal project.
- Crypto or short-term hype packaging.

## Ranking and Outreach

Do not enforce source diversity in the first version. Select the strongest actual signals from the run.

Daily Top target: 10-15 items.

Outreach candidate rule: type-specific score or tier is high enough and there is a public email or clear contact path.

## Output Files

Expected durable outputs:

- Master XLSX: one long-lived table, not daily files.
- Daily Markdown report: one file per date under a report directory.

The implementation may choose exact paths, but they must be stable and shown to the user after each run.

## Codex Response Style

For a completed run, show:

- Coverage: sources attempted, fetched counts, failures.
- Today's Top 10-15.
- Outreach candidates with numbers.
- Links to the master XLSX and daily Markdown report.
- Any partial coverage or failed source clearly.

Keep the response in Chinese unless the user asks otherwise.
