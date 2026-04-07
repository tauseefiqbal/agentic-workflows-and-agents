

import logging
import asyncio
from dotenv import load_dotenv
load_dotenv()
from agents import Agent, Runner, function_tool, trace

# Historical research specialist
history_agent = Agent(
    name="HistoryAgent",
    model="gpt-4",
    instructions=(
        "You are a historical research agent with expertise in Victorian London and Charles Dickens. "
        "You receive queries about Dickens's life and Victorian era context, and you provide factual details and references. "
        "When asked, search your knowledge base or tools for accurate historical information, and return a concise report."
    ),
    tools=[]  # Could add MCP tools for Wikipedia, historical databases, etc.
)

# Fashion and etiquette specialist  
attire_agent = Agent(
    name="AttireAgent",
    model="gpt-4",
    instructions=(
        "You are an expert on Victorian-era attire and etiquette. "
        "Your task is to help a time-traveler blend in. "
        "When asked, suggest appropriate clothing styles, accessories, and social etiquette of 19th-century London (circa 1800s)."
    ),
    tools=[]
)

# Timeline and scheduling specialist
schedule_agent = Agent(
    name="ScheduleAgent", 
    model="gpt-4",
    instructions=(
        "You are a scheduling agent specialized in historical timelines. "
        "Given context about Charles Dickens and Victorian London, determine an ideal date, location, and event for meeting Dickens. "
        "Ensure the suggestion is something that actually happened (e.g., Dickens public appearances) around the target time."
    ),
    tools=[]
)

planner_agent = Agent(
    name="TimeTravelPlanner",
    model="gpt-4", 
    instructions=(
        "You are a planning agent helping a user prepare a time-travel trip to Victorian London to meet Charles Dickens.\n"
        "Break the task into steps and use the specialized agents for each subtask:\n"
        "- Use HistoryAgent for historical facts and Dickens's background.\n"
        "- Use AttireAgent for advice on Victorian clothing and etiquette.\n" 
        "- Use ScheduleAgent for planning when/where to meet Dickens.\n"
        "Only use these tools to get factual information (do not fabricate details yourself). Once you have all the information, compile a final detailed plan for the user."
    ),
    tools=[
        history_agent.as_tool(
            tool_name="HistoryAgent",
            tool_description="Historical research on Dickens and Victorian era"
        ),
        attire_agent.as_tool(
            tool_name="AttireAgent", 
            tool_description="Victorian era attire and etiquette advisor"
        ),
        schedule_agent.as_tool(
            tool_name="ScheduleAgent",
            tool_description="Historical scheduling assistant for Dickens's timeline"
        )
    ]
)



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    user_request = "Plan a time-travel trip to Victorian London to meet Charles Dickens."
    try:
        with trace("TimeTravelPlannerWorkflow"):
            logger.info("Starting agent orchestration")
            result = await Runner.run(planner_agent, user_request)
            logger.info(f"Orchestration completed successfully")
            print(result.final_output)
    except Exception as e:
        logger.error(f"Agent orchestration failed: {e}")

asyncio.run(main())

