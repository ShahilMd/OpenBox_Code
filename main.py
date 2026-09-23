import asyncio

from client.llm_client import LLMClient


async def main() -> None:
    client = LLMClient()
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        }
    ]
    async for event in client.chat_completion(messages, True):
        print(event)
    print("done")
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
