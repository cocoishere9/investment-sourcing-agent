# 投资 Sourcing Agent

这是一个面向 AI / 科技投资 sourcing 的本地 MVP。核心思路是：不同来源产生不同类型的信息，不强行转成同一种结构，而是先识别内容类型，再进入对应处理链路。

## 核心工作流

```text
公开来源采集
  -> 统一外壳 SourceItem
  -> 判断 artifact_type
  -> company / repo / paper / post processor
  -> scoring rubric
  -> memo / digest / outreach draft
  -> 人工审核
```

## 本地运行

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m sourcing_agent.cli run-daily --dry-run
PYTHONPATH=src python3 -m sourcing_agent.cli show-digest
PYTHONPATH=src python3 -m sourcing_agent.cli review-queue
```

更完整的中文说明见：`docs/使用说明.md`。

## 配置文件

- `config/taste_prompt.yaml`：投资偏好、负面信号、阈值。
- `config/scoring_rubrics.yaml`：不同内容类型的打分项、权重和扣分规则。
- `config/sources.yaml`：不同来源和默认 artifact type。

## 文档

- `docs/使用说明.md`：如何运行、如何验收、当前能力边界。
- `docs/架构说明.md`：工作流节点、脚本映射、大模型节点设计、`score.py` 打分规则。
- `docs/执行清单.md`：已完成事项和逐项检查方式。

## 可信边界

- 系统不会自动发邮件，只生成草稿。
- 华人/中国相关判断允许简单启发式，但必须标记为低/中/高置信度。
- 所有高分判断都应保留来源 URL、理由和 evidence。

## 当前状态

这是可运行 MVP，不是生产系统。当前 `run-daily --dry-run` 使用确定性的样例数据，方便验证完整链路；真实来源抓取函数已经按 source 拆开，后续可以逐个接入真实 API key 和网页来源。
