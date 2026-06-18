from sourcing_agent.models import ArtifactType, SourceItem


PROCESSORS = {
    ArtifactType.COMPANY: "company",
    ArtifactType.REPO: "repo",
    ArtifactType.PAPER: "paper",
    ArtifactType.POST: "post",
}


def processor_name_for(item: SourceItem) -> str:
    return PROCESSORS[item.artifact_type]

