# Investment Sourcing Agent

这是一个在 Codex 里运行的 AI / 科技投资 sourcing agent。它的目标不是替代投资判断，而是把每天散落在 YC、GitHub、arXiv、Hacker News 等公开来源里的早期技术信号抓出来，整理成可审阅的候选池，再由 Agent 做语义判断、去重、写日报和准备建联草稿。

一句话说：它是一个“每天帮你发现值得看的 AI infra / robotics / inference / devtools / scientific AI 项目”的工作流。

## 它做什么

这个 agent 主要处理四类机会：

- `company`：YC 公司、早期创业公司、产品页。
- `repo`：GitHub 项目、开源基础设施、开发者工具。
- `paper`：arXiv 论文、研究项目、可商业化的技术方向。
- `post`：HN launch/show/discussion，以及它背后的项目或团队。

它会关注：

- AI infra、agent infrastructure、developer tools。
- inference、edge AI、AI hardware。
- robotics、embodied AI、机器人开发工具。
- scientific AI。
- 华人/中国背景 founder recall 和跨境机会。

它不会自动做投资决策，也不会自动发邮件。所有建联发送都必须经过人工选择和二次确认。

## 项目组成

核心文件分成三层。

### 1. Skill：用户入口和策略

文件：`skills/investment-sourcing-agent/investment-sourcing-agent.skill.md`

这个文件是 Codex 里的可引用 skill。它定义：

- 用户说“运行今日 sourcing”时应触发什么 workflow。
- source query、阈值、主题词、打分偏好、outreach 条件。
- 哪些判断属于 Agent，哪些工作属于脚本。
- 日报去重和 follow-up 的策略边界。

重要原则：skill 负责“规则和操作契约”，不要把这些策略硬编码到脚本里。

### 2. Agent Manual：子 Agent 操作手册

文件：`agents/investment-sourcing-agent/investment-sourcing-agent.agent.md`

这个文件描述 investment sourcing subagent 的行为边界：

- 如何理解不同 artifact type。
- 如何做 novelty review：`new`、`follow_up`、`exclude_previously_reported`。
- 什么时候允许一个已经推过的项目再次出现在日报里。
- master XLSX、raw artifact、daily report 应该如何互相配合。
- Gmail 建联审批边界。

简单说，skill 是入口，agent manual 是操作手册。

### 3. Runner：确定性采集和结构化

文件：`scripts/daily_sourcing_runner.py`

runner 只做确定性的工程执行：

- 从公开来源抓取候选。
- 应用 source-specific threshold。
- 按 `company / repo / paper / post` 打分。
- 更新长期 master XLSX。
- 写出 raw/scored run artifact。

runner 不应该最终决定日报里展示什么。最终日报选择由 Agent 读取 raw artifact、master、历史日报后完成。

推荐模式：

```bash
python3 scripts/daily_sourcing_runner.py --artifact-only
```

`--artifact-only` 会生成候选池和更新 master，但把最终日报选择留给 Agent。

兼容模式：

```bash
python3 scripts/daily_sourcing_runner.py
```

这个模式会生成一个 provisional report，但它只是中间产物；最终报告仍应由 Agent 做 novelty review 后确认或重写。

## 工作流

日常使用时，用户不需要直接操作 CLI。推荐在 Codex 里说：

```text
运行今日 sourcing
```

Agent 应该按这个流程执行：

1. 读取 `investment-sourcing-agent.skill.md`。
2. 读取 `investment-sourcing-agent.agent.md`。
3. 调用 runner 生成今日 raw/scored candidate pool。
4. 读取长期 master XLSX、历史日报和历史 raw artifacts。
5. 对今日高分候选做 novelty review。
6. 排除已经推过且没有新进展的项目。
7. 对有重大新证据的重复项目标记为 `Follow-up`。
8. 写出当天中文 sourcing 日报。
9. 列出 outreach candidates，但不发送邮件。
10. 回到 Codex 对话里展示覆盖情况、Top、建联候选和文件路径。

核心逻辑是：

```text
public sources
  -> deterministic runner
  -> raw/scored candidate pool
  -> master XLSX
  -> Agent novelty review
  -> final daily report
  -> optional outreach drafts
  -> human approval before sending
```

## 输出文件

当前稳定输出包括：

- `data/investment_sourcing_master.xlsx`：长期 master 表，一条机会一行，记录 first/last seen、score、tier、evidence、outreach status 等。
- `data/raw/YYYY-MM-DD-sourcing-run.json`：当天 raw/scored artifact，保留 coverage、filters、failures、items、scored candidates。
- `reports/daily/YYYY-MM-DD-sourcing-digest.md`：当天中文日报，应该由 Agent 经过 novelty review 后形成最终版本。

## 日报去重逻辑

日报不是简单按 URL 去重。Agent 应该做语义判断：

- 同一个公司、repo、paper、产品、HN 外链或研究项目，即使来源不同，也视为已推过。
- 已推过且没有实质新信息的项目，不再进入新日报 Top 或建联候选。
- 如果出现重大新 release、代码/benchmark、traction 变化、融资/YC 状态变化、新 founder/contact 证据，允许作为 `Follow-up` 再推。
- `Follow-up` 必须说明“这次新在哪里”。

这部分判断属于 Agent，不属于 runner。

## 建联边界

系统可以生成英文和中文 outreach draft，但不能自动发送。

发送流程必须是：

1. Agent 展示编号候选。
2. 用户选择，例如“发送 1、3、5”。
3. Agent 复述收件人和标题，并要求最终确认。
4. 用户再次明确确认后，才可以调用 Gmail 发送。
5. 发送结果要写回状态和证据。

## 当前状态

这是一个本地可运行的 Codex workflow，不是生产级 SaaS。它的重点是把投资 sourcing 的操作路径打通：

- skill 管策略和用户意图。
- agent manual 管判断流程和边界。
- runner 管抓取、结构化、初筛和 artifact。
- Codex 对话是用户操作台。

后续更适合增强的方向是：更好的历史 novelty index、更丰富的 founder/background enrichment、更稳定的 source adapter，以及更清晰的 review/outreach 队列。
