import asyncio
import json
from types import SimpleNamespace

from integration.model_client import CachedModelClient
from src.agent_runtime import AgentRuntime
from src.llm_client import LLMResponse
from src.member_context import build_member_context
from src.models import MemberAgent


class RecordingClient:
    config = SimpleNamespace(provider="deepseek", model="deepseek-flash", base_url="test")

    def __init__(self):
        self.requests = []

    def chat_with_metadata(self, messages, temperature):
        self.requests.append(messages)
        return LLMResponse('{"ok":true}', {
            "usage_metadata": {"input_tokens": 50, "output_tokens": 4},
            "response_metadata": {"token_usage": {"prompt_cache_hit_tokens": 30, "prompt_cache_miss_tokens": 20}},
        })


def test_shared_prefix_keeps_private_views_and_distinct_member_answers(tmp_path):
    transport = RecordingClient()
    client = CachedModelClient(transport, tmp_path, prefix_cache=True)
    runtime = AgentRuntime(client)
    runtime.context_resolver = lambda entity: {"public": {"currency": "CNY"}, "own_state": entity}
    company = SimpleNamespace(company_name="C", company_role="contractor")

    def ask(name, entity):
        member = MemberAgent(name, name, entity, "contractor", "department", "manager", "profile", [], "", "")
        prompt = build_member_context("bid", "review", company, "P1", member, "common task", [],
                                      prefix_cache=runtime.prefix_cache)
        return asyncio.run(runtime.for_entity(entity).ask_json_async("Read facts", "AGENT_MESSAGE", prompt))

    for name, entity in [("Alice", "private-A"), ("Bob", "private-A"), ("Alice", "private-B"), ("Alice", "private-A")]:
        assert ask(name, entity) == {"ok": True}
    first, second, other = [request[1]["content"] for request in transport.requests]
    assert first.split("\nAgent: ")[0] == second.split("\nAgent: ")[0]
    assert "common task" in first.split("\nAgent: ")[0]
    assert "Agent: Alice" in first and "Agent: Bob" in second
    facts = other.split("\n", 3)[2]
    assert json.loads(facts)["own_state"] == "private-B" and "private-A" not in other
    usage = client.usage()
    assert (usage["requests"], usage["cache_hits"]) == (3, 1)
    assert (usage["prompt_cache_hit_tokens"], usage["prompt_cache_miss_tokens"]) == (90, 60)
