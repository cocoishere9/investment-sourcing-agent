---
name: investment-sourcing-agent
description: Use when running, inspecting, or operating AI and technology investment sourcing workflows; finding AI infra, robotics, GitHub, arXiv, YC, HN signals; reviewing daily sourcing reports; or drafting founder outreach.
---

# investment-sourcing-agent Skill

- Canonical skill name: `investment-sourcing-agent`
- Display name: `Investment Sourcing Agent`
- Primary file: `skills/investment-sourcing-agent/investment-sourcing-agent.skill.md`
- Search aliases: `投资 sourcing agent`, `今日 sourcing`, `AI investment sourcing`, `sourcing 日报`, `founder outreach`

Use this skill when the user asks to run, inspect, design, or operate the investment sourcing workflow for AI, AI hardware, robotics, AI infrastructure, agent infrastructure, inference, scientific AI, GitHub projects, arXiv papers, YC companies, HN launches, founder discovery, or outreach.

This skill is the user-facing entrypoint. Do not tell the user to operate a CLI. You may use local deterministic modules, scripts, or connectors underneath, but Codex and this skill are the operating surface.

## Responsibility Boundary

Keep one clear division of labor.

- **This skill owns the user intent and operating contract.** It maps natural language to workflow actions, states the sourcing taste, approval boundaries, output expectations, and what must be shown back to the user.
- **This skill owns adjustable policy.** Numeric thresholds, source quality filters, Top count, outreach eligibility, source queries, theme vocabularies, and report novelty policy live in the machine-readable `runner_policy` block below.
- **Python or local modules own deterministic execution.** Scripts fetch public sources, read `runner_policy` from this skill, apply configured filters, score rows, update XLSX, and write raw candidate artifacts. They may produce a provisional convenience report, but they must not own final report selection, historical dedupe, semantic novelty judgment, or follow-up judgment.
- **Codex owns orchestration and judgment.** Codex reads this skill, reads the subagent manual, checks the available implementation, runs the deterministic layer, performs Agent-native novelty review against historical reports/master/raw artifacts, writes the final Chinese daily report, verifies artifacts, and summarizes the result in Chinese.

Do not maintain competing rule sets in both `investment-sourcing-agent.skill.md` and Python. When the user changes taste or thresholds, update `runner_policy` in this skill first. Change Python only when the runner cannot yet interpret the policy.

## Load Order

Before acting, read the subagent manual:

`agents/investment-sourcing-agent/investment-sourcing-agent.agent.md`

If the file is missing, continue with this skill's rules and tell the user that the subagent manual is missing.

## Core Contract

- Codex is the operating console.
- The first version is manual or manually triggered. Do not create a recurring automation unless the user explicitly asks later.
- Keep the workflow modular. Each stage can run alone or as part of `daily_run`.
- Use real public data only. Never fabricate missing source data.
- Fetch a candidate pool from each source, then apply source-specific quality thresholds before scoring.
- Keep at most 20 qualified items per source by default unless the user explicitly overrides this.
- Maintain one long-lived master XLSX table.
- Write a concise Chinese date-specific Markdown report after Agent-native novelty review.
- Draft both English and Chinese outreach emails only for eligible outreach candidates.
- Gmail sending requires numbered user selection plus a second explicit confirmation.

## Standard Actions

Map natural-language requests to these actions.

### `daily_run`

Run the full first-version workflow:

1. Read `runner_policy` from this skill for source thresholds, source queries, taste terms, outreach rules, and Top count.
2. Run the deterministic layer in raw/scored artifact mode when available, such as `--artifact-only`; do not rely on runner-selected Top output as the final report.
3. Fetch configured sources.
4. Apply source-specific quality thresholds before scoring.
5. Process qualified items by artifact type.
6. Score items with type-specific rubrics.
7. Update the master XLSX without duplicating existing rows.
8. Read today's raw/scored candidate artifact, the long-lived master XLSX, prior daily reports, and any available raw artifacts.
9. Perform Agent-native novelty review: classify each strong candidate as new, follow-up, or previously reported/excluded.
10. Render the final Chinese daily Markdown report from the Agent-selected new and allowed follow-up items.
11. Draft bilingual outreach only for eligible candidates that survive novelty review.
12. Show coverage, novelty counts, Top summary, outreach candidates, and artifact links in Codex.

### `fetch_only`

Fetch source data without scoring or outreach. Use when the user asks to refresh sources, inspect source health, or run only a subset such as GitHub and arXiv.

### `process_only`

Transform fetched raw items into typed signals: company, repo, paper, or post.

### `score_only`

Score or rescore processed items using the current taste and rubric rules.

### `show_digest`

Show the current day's concise Top list in Codex and link to the Markdown report.

### `draft_outreach`

Generate bilingual outreach drafts only for candidates that meet the outreach rule: high enough type-specific score or tier, public email or clear contact path, and suspected 中国/华人 signal.

### `review_outreach`

Show numbered pending outreach candidates. For each candidate, include recipient, source item, why it was selected, the suspected 中国/华人 signal and confidence, English subject/body, Chinese subject/body, and evidence links.

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

## Source Quality Thresholds

The workflow should not show every fetched item. It should first filter for signals that a human investor can realistically review.

Default threshold policy:

- **GitHub repos:** include only repositories with meaningful attention or momentum, such as high star count, strong recent star velocity, or a very new repo with unusually fast early attention. Low-star, low-discussion repos should not enter the daily Top.
- **Hacker News posts:** include only posts with a real external artifact and meaningful discussion or points. Low-engagement posts without a traceable entity should be dropped.
- **arXiv papers:** include only recent papers that strongly match preferred themes such as agent infrastructure, inference, robotics, AI hardware, scientific AI, or implementation-heavy AI systems.
- **YC/company sources:** include only active or early-stage companies with strong theme fit and enough product/founder evidence for follow-up.

The block below is the source of truth for the deterministic runner. Keep it valid JSON.

```json runner_policy
{
  "version": 1,
  "max_qualified_items_per_source": 20,
  "top_limit": 12,
  "source_queries": {
    "yc": ["AI", "robotics", "infrastructure", "developer tools", "inference", "agents", "MCP", "scientific AI", "hardware AI"],
    "github": [
      "ai agent infrastructure stars:>10 pushed:>=2026-06-01",
      "robotics ai hardware stars:>5 pushed:>=2026-06-01",
      "ai inference robotics stars:>10 pushed:>=2026-06-01",
      "mcp agent infrastructure stars:>5 pushed:>=2026-06-01"
    ],
    "arxiv": "(all:agent OR all:robotics OR all:inference OR all:on-device) AND (cat:cs.AI OR cat:cs.LG OR cat:cs.RO)",
    "hacker_news": ["AI agent launch", "AI infrastructure", "robotics", "inference", "developer tools AI", "MCP"]
  },
  "source_thresholds": {
    "github": {
      "min_stars": 300,
      "velocity_min_stars": 50,
      "min_stars_per_day": 3.0,
      "new_repo_days": 14,
      "new_repo_min_stars": 30
    },
    "hacker_news": {
      "require_external_url": true,
      "min_points": 30,
      "min_comments": 10,
      "launch_min_points": 15
    },
    "arxiv": {
      "max_age_days": 14,
      "min_theme_tags": 2
    },
    "yc": {
      "allowed_batches": ["Fall 2025", "Spring 2025", "Spring 2026", "Summer 2025", "Summer 2026", "Winter 2026"],
      "require_active": true,
      "require_early": true,
      "max_team_size": 20,
      "min_theme_tags": 2
    }
  },
  "theme_terms": {
    "agent_infra": ["agent", "agents", "agentic", "mcp", "tool-calling", "coding agent", "computer-use", "sandbox"],
    "ai_infra": ["infrastructure", "infra", "platform", "runtime", "scheduler", "cloud", "vm", "observability", "eval"],
    "inference": ["inference", "serving", "latency", "throughput", "on-device", "edge", "jetson", "gpu"],
    "robotics": ["robot", "robotics", "humanoid", "urdf", "embodied", "manipulation", "autonomous"],
    "ai_hardware": ["hardware", "semiconductor", "chip", "device", "sensor", "power supply", "edge"],
    "devtools": ["developer tools", "devtool", "sdk", "cli", "api", "ide", "github", "open source"],
    "scientific_ai": ["scientific", "biology", "chemistry", "drug", "materials", "lab", "protein"]
  },
  "background_terms": ["openai", "deepmind", "anthropic", "google", "meta", "nvidia", "tesla", "netlify", "stanford", "mit", "cmu", "carnegie mellon", "berkeley", "princeton", "harvard", "oxford", "cambridge", "tsinghua", "peking university", "pku", "phd", "csail", "bair", "robotics institute", "acquired", "founder", "principal architect"],
  "china_terms": ["china", "chinese", "beijing", "shanghai", "shenzhen", "tsinghua", "peking university", "pku", "mandarin", "cross-border"],
  "romanized_chinese_name_hints": ["wang", "zhang", "li", "liu", "chen", "yang", "huang", "zhao", "zhou", "wu", "xu", "sun", "ma", "gao", "lin", "he", "luo", "wei", "xin", "hao", "yi", "xue", "qing", "jun", "liang"],
  "outreach": {
    "min_score": 75,
    "require_contact_path": true,
    "require_suspected_china_signal": true,
    "max_candidates": 10,
    "draft_languages": ["en", "zh"]
  },
  "report": {
    "language": "zh",
    "include_outreach_drafts_in_top": false,
    "agent_novelty_review": {
      "default_exclude_previously_reported": true,
      "history_sources": ["prior_daily_reports", "master_xlsx", "raw_run_artifacts"],
      "allow_follow_up_for": [
        "major_product_release",
        "new_open_source_code_or_benchmark",
        "material_traction_or_star_velocity_change",
        "funding_or_yc_batch_update",
        "new_founder_or_contact_evidence",
        "important_new_hn_discussion_or_research_result"
      ]
    }
  }
}
```

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

Daily Top target: 10-12 concise entries unless the user asks for more.

## Agent-Native Novelty Review

Final report selection belongs to Codex/Agent, not the deterministic runner.

Before writing the daily report, Codex must compare today's strong candidates against prior daily reports, the master XLSX, and prior raw artifacts when available. This is a semantic review, not only exact URL matching.

Default behavior:

- Do not include opportunities that were already shown in a previous daily report.
- Treat the same company, repository, paper, product, or external artifact as previously reported even if it appears through a different source such as HN, GitHub, YC, arXiv, or a company page.
- Allow a previously reported item only as an explicit follow-up when there is material new information, such as a major release, new code or benchmark, meaningful traction change, funding or YC batch update, new founder/contact evidence, or important new technical discussion.
- Label allowed repeats as `Follow-up`, not as new discoveries, and explain the new evidence.
- Keep excluded repeats out of both the daily Top and outreach candidates unless they qualify as follow-ups.

Do not implement this novelty policy as a hardcoded filter in the runner. The runner can expose facts and candidate metadata; the Agent performs the judgment and writes the final report.

Outreach candidate rule:

- high enough type-specific score or tier;
- public email or clear contact path;
- suspected 中国/华人 signal is present.

Treat suspected 中国/华人 as a sourcing recall signal, not a verified identity claim. Romanized-name matching is allowed only as low-confidence recall and must be labeled as such.

Do not include outreach drafts inside every Top entry. Show drafts only in the outreach candidate section.

## Output Files

Expected durable outputs:

- Master XLSX: one long-lived table, not daily files.
- Raw run artifact with fetched items, scored candidate pool, coverage, filters, failures, and evidence fields.
- Daily Markdown report: one final Agent-authored file per date under a report directory.

The implementation may choose exact paths, but they must be stable and shown to the user after each run.

Avoid mixing historical low-quality rows with the current day's filtered view. The master table may be long-lived, but each run should preserve enough fields or raw artifacts to distinguish current-run qualified items from older rows. If a deterministic runner emits a provisional report, Codex must treat it as an intermediate artifact and overwrite or replace it with the Agent-selected final report.

## Codex Response Style

For a completed run, show:

- Coverage: sources attempted, qualified counts after threshold filtering, and failures.
- Novelty review: new items, follow-ups, excluded repeats, and any uncertainty.
- Today's concise Top list.
- Outreach candidates with numbers.
- Links to the master XLSX and daily Markdown report.
- Any partial coverage or failed source clearly.

Keep the response in Chinese unless the user asks otherwise.
