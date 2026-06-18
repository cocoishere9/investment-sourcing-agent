def daily_command() -> str:
    return "PYTHONPATH=src python3 -m sourcing_agent.cli run-daily"


def codex_automation_prompt() -> str:
    return (
        "Run the investment sourcing daily workflow, then report the digest summary "
        "and any generated outreach drafts that need human approval."
    )

