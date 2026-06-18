from sourcing_agent.models import OutreachDraft, ProcessedSignal


DEFAULT_INSTITUTION_EN = "Frontier Bridge Ventures"
DEFAULT_INSTITUTION_ZH = "前沿桥资本"


def choose_language(signal: ProcessedSignal) -> str:
    if signal.china_affinity in {"medium", "high"}:
        return "zh"
    return "en"


def render_outreach(
    signal: ProcessedSignal,
    language: str = None,
    sender_name: str = "Kexin",
    institution_en: str = DEFAULT_INSTITUTION_EN,
    institution_zh: str = DEFAULT_INSTITUTION_ZH,
) -> OutreachDraft:
    language = language or choose_language(signal)
    project = signal.item.title
    source = signal.item.source
    specific_signal = signal.summary
    if language == "zh":
        subject = "想就 {project} 做一次技术交流".format(project=project)
        body = """你好，

我是在 {source} 上看到 {project} 的，尤其是「{specific_signal}」这一点让我们很感兴趣。我们最近一直在系统性关注 AI 基础设施、机器人/具身智能、AI 硬件、开发者工具，以及中美/亚洲市场之间的技术商业化机会。

我来自{institution_zh}（{institution_en}），我们是一家关注早期前沿科技的投资与研究机构。我们通常会先从技术交流开始，了解团队正在解决的问题，也分享一些我们在市场、客户和资本方面的观察。

如果你方便的话，下周是否可以约 20 分钟简单聊聊？这次主要想请教你们的技术路线和产品进展，也看看未来是否有合作或投资交流的可能。

祝好，
{sender_name}
{institution_zh} {institution_en}
""".format(
            source=source,
            project=project,
            specific_signal=specific_signal,
            institution_zh=institution_zh,
            institution_en=institution_en,
            sender_name=sender_name,
        )
    else:
        subject = "Technical exchange around {project}".format(project=project)
        body = """Hi,

I came across {project} through {source}, especially this signal: {specific_signal}. The work looks relevant to areas we have been studying closely, including AI infrastructure, robotics, AI hardware, developer tools, and cross-border commercialization.

I am with {institution_en}, an early-stage investment and research-focused firm looking at frontier AI and technology opportunities between the US and Asia. We often start with technical conversations before discussing any formal investment or partnership angle.

Would you be open to a 20-minute conversation sometime next week? I would love to learn more about what you are building and share a few perspectives from our side as well.

Best,
{sender_name}
{institution_en}
""".format(
            source=source,
            project=project,
            specific_signal=specific_signal,
            institution_en=institution_en,
            sender_name=sender_name,
        )
    return OutreachDraft(signal=signal, language=language, subject=subject, body=body)

