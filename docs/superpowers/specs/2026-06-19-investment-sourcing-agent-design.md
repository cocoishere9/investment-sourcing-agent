# Investment Sourcing Agent Design

Date: 2026-06-19

Status: Approved for implementation planning

## 1. Goal

Build a Codex-operated investment sourcing subagent for AI and technology investing. The first version should run an end-to-end lightweight workflow while keeping every stage independently triggerable.

The agent should help discover and triage public signals from sources such as YC, GitHub, arXiv, Hacker News, and configured webpages or RSS feeds. It should update a durable master table, write readable Markdown reports, draft bilingual outreach emails, and send selected Gmail messages only after human approval.

## 2. Key Decisions From Discussion

- Entry point: Codex plus a custom skill, not a user-facing CLI.
- Agent structure: one total-control skill plus a subagent manual plus local deterministic modules underneath.
- Subagent manual location: `agents/investment-sourcing-agent/AGENTS.md`, explicitly scoped to this subagent only.
- Skill location: `skills/investment-sourcing-agent/SKILL.md`.
- Source scope: high-certainty sources first: YC, GitHub, arXiv, Hacker News, and configured webpages or RSS.
- Per-source cap: 20 fetched items by default.
- Scheduling: design for future scheduling, but do not create a real recurring automation in the first version.
- Data table: one long-lived XLSX master table. Do not create a new table every day.
- Markdown: generate detailed entries for all daily Top items in the same date-specific Markdown report.
- Digest: Codex shows daily Top 10-15 and actionable candidates; full data remains in the XLSX.
- Outreach: draft both English and Chinese emails. The user decides which language and which candidates to send.
- Sending: Gmail connector after numbered selection plus a second explicit confirmation.
- Ranking: do not force source diversity in the first version. Show the strongest actual signals.
- 华人/中国相关: use broad recall signals and record the observed reason. Do not present it as verified identity.

## 3. Architecture

```text
Codex conversation
  -> investment-sourcing-agent skill
  -> subagent manual and standard actions
  -> local deterministic modules/tools
  -> source fetchers
  -> typed processors
  -> type-specific scorers
  -> master XLSX updater
  -> Markdown report renderer
  -> outreach drafter
  -> Gmail review/send flow
```

The custom skill is the product surface. Local modules are the deterministic execution layer. The user should not need to remember commands. The agent may use scripts or Python modules internally, but it reports results back through Codex and durable files.

## 4. Standard Actions

The skill maps natural-language requests to these stable actions:

| Action | Purpose |
| --- | --- |
| `daily_run` | Run fetch, process, score, table update, Markdown report, outreach draft, and Codex summary. |
| `fetch_only` | Fetch configured sources or a selected subset. |
| `process_only` | Convert raw fetched items into typed signals. |
| `score_only` | Score typed signals with current rubrics. |
| `show_digest` | Show the current daily Top summary in Codex. |
| `draft_outreach` | Generate bilingual outreach drafts for eligible candidates. |
| `review_outreach` | Show numbered draft candidates for human review. |
| `send_selected` | Send selected Gmail messages only after second confirmation. |
| `backfill_date` | Repair or rerun a specific date. |
| `rescore_master` | Recalculate historical scores after taste/rubric changes. |

These are not user-facing CLI commands. They are stable internal intent labels so Codex can orchestrate the workflow reliably.

## 5. Source Design

### Stable first-version sources

| Source | First-version approach | Notes |
| --- | --- | --- |
| GitHub | Public repository search and repository metadata | GitHub REST API can be used for public data. Unauthenticated calls are limited; authenticated PAT use increases quota. Official docs: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api |
| arXiv | Official arXiv API | Respect arXiv API etiquette and rate limits. Docs: https://info.arxiv.org/help/api/user-manual.html and https://info.arxiv.org/help/api/tou.html |
| Hacker News | Official Firebase API for items and Algolia HN Search for keyword search | HN API: https://github.com/HackerNews/API. Algolia search: https://hn.algolia.com/api |
| YC | Startup Directory page or documented public fallback | YC does not provide a stable official public API. Treat this source as semi-stable and report failures clearly. Directory: https://www.ycombinator.com/companies |
| Webpage/RSS | Only configured sources | Use for targeted VC pages, research blogs, launch pages, or RSS feeds later. |

### Source rules

- Fetch no more than 20 items per source by default.
- Record source coverage, counts, and failures.
- Continue other sources if one source fails.
- Distinguish "no data", "not fetched", and "fetch failed".
- Do not fabricate missing data.

## 6. Artifact Types

The system routes every fetched item into one artifact type:

- `company`: YC companies, portfolio pages, company homepages.
- `repo`: GitHub repositories and open-source projects.
- `paper`: arXiv papers and research project pages.
- `post`: HN posts, launch posts, and other discussion items.

Do not force every item into a company schema. Each type gets its own processor and scoring rubric.

## 7. Taste and Scoring

### Core taste

The agent should prefer:

- AI infra, DevTools, and agent infrastructure.
- Inference, AI hardware, and edge AI.
- Robotics.
- Scientific AI.
- 华人/中国 founder recall.
- Cross-border China or global opportunities.

The strongest priority is founder, author, or maintainer background. Relevant signals include:

- Ivy League, Stanford, MIT, CMU, Berkeley, Oxbridge, 清华, 北大, and similarly strong technical universities.
- Core labs and research groups such as Stanford HAI, MIT CSAIL, Berkeley BAIR, CMU Robotics Institute, Princeton NLP, 清华姚班, 智源, 上海 AI Lab, plus configurable additions.
- Top conference papers, open-source impact, technical depth, AI infra or robotics experience, hardware/inference expertise, or clear founder-like shipping behavior.

These signals are additive, not mandatory. The agent should not reject strong non-credentialed builders.

### Score model

Use type-specific 0-100 rubrics. A company score, repo score, paper score, and post score are not treated as perfectly comparable. For mixed daily Top ranking, use the type-specific score, tier, evidence quality, and actionability.

Suggested tiers:

- `A`: 85-100
- `B`: 70-84
- `C`: 55-69
- `Watch`: below 55 or insufficient evidence

### Company rubric

| Dimension | Weight |
| --- | ---: |
| Founder background | 35 |
| Theme fit | 20 |
| Technical asset or product depth | 20 |
| Product clarity or traction | 15 |
| Contactability | 10 |

### Repo rubric

| Dimension | Weight |
| --- | ---: |
| Maintainer background | 25 |
| Technical depth | 25 |
| Adoption or momentum | 20 |
| Theme fit | 15 |
| Commercialization and contactability | 15 |

### Paper rubric

| Dimension | Weight |
| --- | ---: |
| Author or lab background | 30 |
| Novelty and technical relevance | 25 |
| Implementation or commercialization path | 20 |
| Theme fit | 15 |
| Contactability or project link | 10 |

### Post rubric

| Dimension | Weight |
| --- | ---: |
| Traceable entity quality | 30 |
| Technical or product detail | 25 |
| Founder or background clue | 20 |
| Engagement and freshness | 15 |
| Theme fit and contactability | 10 |

### Negative signals

Apply penalties or mark as not outreach-ready for:

- Pure AI wrapper.
- No technical artifact.
- No public contact path.
- Too late stage.
- Funding news without product detail.
- Obvious big-company internal project.
- Crypto or short-term hype packaging.

### Outreach threshold

An item becomes an outreach candidate when:

- it reaches a strong enough type-specific score or tier, and
- it has a public email or clear contact path.

The first version should default to score >= 75 plus public contact path, while allowing type-specific overrides later.

## 8. Data Model and Durable Outputs

### Master XLSX

Maintain one long-lived XLSX master table. Do not create a new master file per day.

First-version columns:

| Column | Meaning |
| --- | --- |
| `first_seen_date` | First date the item entered the table. |
| `last_seen_date` | Most recent date the item appeared or was updated. |
| `source` | Source name, such as GitHub, arXiv, HN, YC. |
| `type` | Artifact type: company, repo, paper, post. |
| `name_or_title` | Company, repo, paper, or post title. |
| `url` | Canonical URL. |
| `score` | Type-specific 0-100 score. |
| `tier` | A, B, C, or Watch. |
| `outreach_status` | Current outreach state. |
| `founder_or_contact` | Founder, author, maintainer, or public contact. |
| `china_signal` | Broad China/华人/cross-border signal and reason. |
| `founder_background_signal` | School, lab, company, paper, OSS, or shipping evidence. |
| `theme_tags` | Matched taste themes. |
| `one_line_summary` | Short human-readable summary. |
| `evidence` | Evidence URLs or compact evidence notes. |
| `markdown_anchor` | Link or anchor into the daily Markdown report. |
| `notes` | User-editable notes. |

Outreach status values:

- `not_candidate`
- `draft_ready`
- `selected`
- `confirmation_pending`
- `sent`
- `skipped`
- `failed`

### Daily Markdown report

Generate one report file per date, for example:

```text
reports/daily/2026-06-19-sourcing-digest.md
```

Each Top item should include:

- One-line summary.
- Why it is worth reading.
- Founder, author, or maintainer background.
- Evidence links.
- Suggested next action.
- English outreach draft.
- Chinese outreach draft.

Do not add a separate risk section in the first version.

### Codex conversation output

After a run, Codex should show:

- Sources attempted and fetched counts.
- Any source failures or partial coverage.
- Today's Top 10-15.
- Why each item was selected.
- Outreach candidate numbers.
- Links to the master XLSX and daily Markdown report.

## 9. Deduplication and Updates

Use stable source IDs where available:

- GitHub: repository full name or canonical repo URL.
- arXiv: arXiv ID.
- HN: item ID.
- YC: company slug or canonical company URL.
- Web/RSS: canonical URL.

When an item reappears, update `last_seen_date`, score, evidence, report anchor, and status as needed. Do not duplicate rows unless the canonical identity is genuinely different.

## 10. Outreach and Gmail Flow

The agent drafts both English and Chinese email versions for each outreach candidate. The default tone is technical exchange first, with investment interest expressed lightly and concretely.

Required send flow:

1. `draft_outreach` creates bilingual drafts.
2. `review_outreach` shows numbered candidates.
3. User chooses numbers, such as "发送 1、3、5".
4. Agent repeats exact recipients and subjects.
5. Agent asks for final confirmation.
6. Only after explicit confirmation does the agent call Gmail tools.
7. Agent records send result, timestamp, recipient, subject, source item, final body version, and Gmail message/thread ID when available.

No automatic sending is allowed.

## 11. Error Handling

Every fetch, report, table update, and Gmail action should expose failure information:

- action or source
- timestamp
- failed query or item
- reason
- whether the issue is missing data, not fetched, or fetch failed
- recommended retry action

If a source fails, the run may still complete with partial coverage. The Codex summary must say this clearly.

## 12. Verification Criteria

A first-version run is complete only if:

- The actual configured sources were attempted.
- Per-source counts and failures are visible.
- The master XLSX exists and was updated.
- The daily Markdown report exists and contains Top item entries.
- Codex displays the same Top items as the generated report.
- Outreach candidates have public contact paths.
- No email is sent without second confirmation.

## 13. Implementation Notes

Existing project code already contains a local MVP shape with sources, processors, scoring, outputs, review, scheduler, and tests. The next implementation plan should adapt that structure toward the new Codex-skill entrypoint and XLSX/Markdown/Gmail workflow without making CLI the primary user interface.

Implementation should keep deterministic engineering logic in local modules and keep model judgment in extraction, memo writing, email drafting, and evidence-aware summarization.
