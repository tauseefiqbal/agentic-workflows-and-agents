import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents.mcp import MCPServerStdio

from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel


async def main():
    load_dotenv()

    # MCP server configurations
    context7_params = {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp@latest"]
    }
    mem0_params = {
        "command": "npx",
        "args": ["-y", "@pinkpixel/mem0-mcp"],
        "env": {
            "MEM0_API_KEY": os.getenv("MEM0_API_KEY", ""),
            "DEFAULT_USER_ID": os.getenv("DEFAULT_USER_ID", "alice")
        }
    }

    context7_server = MCPServerStdio(params=context7_params, name="context7", client_session_timeout_seconds=60)
    mem0_server = MCPServerStdio(params=mem0_params, name="mem0", client_session_timeout_seconds=60)

    async with context7_server, mem0_server:
        # List available tools to verify connection
        tools = await context7_server.list_tools()
        print("Context7 tools:", [t.name for t in tools])
        tools = await mem0_server.list_tools()
        print("Mem0 tools:", [t.name for t in tools])

        # Create an OpenAI chat model
        client = AsyncOpenAI()
        model = OpenAIChatCompletionsModel(model="gpt-4", openai_client=client)

        # Define the agent with instructions
        agent = Agent(
            name="Assistant",
            model=model,
            instructions=(
                "You have two special tools available:\n"
                "- `context7` for fetching up-to-date documentation.\n"
                "- `mem0` for recalling past facts or storing new information.\n\n"
                "Use `context7` whenever the user asks for technical info. "
                "Use `mem0` to remember important details and recall them later. "
                "Always combine retrieved knowledge with your reasoning."
            ),
            mcp_servers=[context7_server, mem0_server]
        )

        print("\nAgent ready! Type your message (or 'quit' to exit).\n")

        try:
            while True:
                user_input = input("You: ").strip()
                if not user_input or user_input.lower() in ("quit", "exit"):
                    break

                result = await Runner.run(agent, input=user_input)
                print(f"Agent: {result.final_output}\n")
        except KeyboardInterrupt:
            pass

        print("Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass