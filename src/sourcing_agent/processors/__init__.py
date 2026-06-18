from sourcing_agent.models import ArtifactType, ProcessedSignal, SourceItem
from sourcing_agent.processors.company import process_company
from sourcing_agent.processors.paper import process_paper
from sourcing_agent.processors.post import process_post
from sourcing_agent.processors.repo import process_repo


def process_item(item: SourceItem) -> ProcessedSignal:
    if item.artifact_type == ArtifactType.COMPANY:
        return process_company(item)
    if item.artifact_type == ArtifactType.REPO:
        return process_repo(item)
    if item.artifact_type == ArtifactType.PAPER:
        return process_paper(item)
    if item.artifact_type == ArtifactType.POST:
        return process_post(item)
    raise ValueError("Unsupported artifact type: " + item.artifact_type.value)

