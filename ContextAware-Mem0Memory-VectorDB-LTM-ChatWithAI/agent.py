import os
os.environ["MEM0_TELEMETRY"] = "false"

from openai import OpenAI
from mem0 import Memory
from dotenv import load_dotenv

load_dotenv()

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"collection_name": "mem0", "embedding_model_dims": 1536, "on_disk": True, "path": "./qdrant_data"},
    },
}

openai_client = OpenAI()
memory = Memory.from_config(config)


def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant memories
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(
        f"- {entry.get('memory', '')}" for entry in relevant_memories.get("results", [])
    ).strip()

    if not memories_str:
        memories_str = "- No relevant memories found."

    print("\nRelevant memories:")
    print(memories_str)
    print()

    # Generate assistant response with streaming
    system_prompt = (
        "You are a helpful AI. Answer the question based on query and memories.\n"
        f"User Memories:\n{memories_str}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    assistant_response = ""
    print("AI: ", end="", flush=True)

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            assistant_response += delta
            print(delta, end="", flush=True)

    print("\n")

    # Save conversation into memory
    memory.add(
        [
            {"role": "user", "content": message},
            {"role": "assistant", "content": assistant_response},
        ],
        user_id=user_id,
        metadata={"source": "demo"},
    )

    return assistant_response


def main():
    print("Chat with AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        chat_with_memories(user_input)


if __name__ == "__main__":
    main()