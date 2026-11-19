from __future__ import annotations

from src.discussion_context import recent_discussion_context
from src.models import Company, DiscussionMessage, MemberAgent


def build_member_context(
    stage: str,
    round_type: str,
    company: Company,
    package_id: str,
    agent: MemberAgent,
    context: str,
    previous: list[DiscussionMessage],
    memory: list[DiscussionMessage] | None = None,
    *, prefix_cache: bool = False,
) -> str:
    member = (
        f"Agent: {agent.agent_name}, {agent.position}, {agent.department}\n"
        f"Personal profile: {agent.personal_profile}\n"
        f"Decision authority: {agent.decision_authority}\n"
        f"Communication style: {agent.communication_style}\n"
        f"Responsibilities: {agent.responsibilities}"
    )
    company_package = f"Company: {company.company_name} ({company.company_role})\nPackage: {package_id}"
    history = f"Previous messages to consider:\n{recent_discussion_context(previous)}"
    recall = f"Relevant earlier company memory:\n{recent_discussion_context(memory or [], 5)}"
    if prefix_cache:
        return "\n".join((company_package, f"Stage: {stage}", f"Context: {context}",
                          f"Round type: {round_type}", history, member, recall))
    return "\n".join((f"Stage: {stage}", f"Round type: {round_type}", company_package,
                      member, f"Context: {context}", recall, history))
