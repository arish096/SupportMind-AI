from google.adk.agents import SequentialAgent

from .customer_agent import customer_agent
from .memory_agent import memory_agent
from .resolution_agent import resolution_agent
from .review_agent import review_agent


coordinator_agent = SequentialAgent(
    name="supportmind_workflow",

    description=(
        "Runs the complete SupportMind AI customer "
        "support workflow in sequence."
    ),

    sub_agents=[
        customer_agent,
        memory_agent,
        resolution_agent,
        review_agent
    ]
)