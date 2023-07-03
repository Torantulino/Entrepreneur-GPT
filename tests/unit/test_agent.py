from unittest.mock import MagicMock

import pytest

from autogpt.agent import Agent
from autogpt.config import AIConfig
from autogpt.config.config import Config
from autogpt.core.agent.simple import SimpleAgent
from autogpt.core.runner.client_lib.logging import get_client_logger
from autogpt.workspace.workspace import Workspace


@pytest.fixture
def agent(config: Config):
    ai_name = "Test AI"
    memory = MagicMock()
    next_action_count = 0
    command_registry = MagicMock()
    ai_config = AIConfig(ai_name=ai_name)
    system_prompt = "System prompt"
    triggering_prompt = "Triggering prompt"
    client_logger = get_client_logger()
    agent_settings = SimpleAgent.compile_settings(client_logger, {})
    workspace = Workspace(
        settings=agent_settings.workspace, logger=client_logger
    )

    agent = Agent(
        ai_name=ai_name,
        memory=memory,
        next_action_count=next_action_count,
        command_registry=command_registry,
        ai_config=ai_config,
        config=config,
        system_prompt=system_prompt,
        triggering_prompt=triggering_prompt,
        workspace=workspace,
    )
    return agent


def test_agent_initialization(agent: Agent):
    assert agent.ai_name == "Test AI"
    assert agent.memory == agent.memory
    assert agent.history.messages == []
    assert agent.next_action_count == 0
    assert agent.command_registry == agent.command_registry
    assert agent.ai_config == agent.ai_config
    assert agent.system_prompt == "System prompt"
    assert agent.triggering_prompt == "Triggering prompt"


# More test methods can be added for specific agent interactions
# For example, mocking chat_with_ai and testing the agent's interaction loop
