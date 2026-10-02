import asyncio
import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError

from client.response import EventType, StreamEvent, TextDelta, TokenUsage

load_dotenv(Path(__file__).resolve().parent.parent / ".env", interpolate=False)


class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._api_key = os.getenv("OPENROUTER_API_KEY")
        self._base_url = os.getenv("OPENROUTER_BASE_URL")
        self._model = os.getenv("OPENROUTER_MODEL")
        self._max_retries: int|None = int(os.getenv("MAX_RETRY"))

        if not self._api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in .env")
        if not self._base_url:
            raise ValueError("OPENROUTER_BASE_URL is not set in .env")
        if not self._model:
            raise ValueError("OPENROUTER_MODEL is not set in .env")

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        stream: bool = True,
    ) -> AsyncGenerator[StreamEvent, None]:


        client = self.get_client()

        kwargs = {
                    "model": self._model,
                    "messages": messages,
                    "stream": stream,
                }
        for attemp in range(self._max_retries + 1):
            try:
                if stream:
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                return
            
            except RateLimitError as e:
                if attemp < self._max_retries:
                    #  But i will add exponential time that will increase 
                    wait_time = 2**attemp
                    # 2s
                    # 4s

                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type = EventType.ERROR,
                        error= f"Rate limiting exceeded {e}",
                    )
                    return

            except APIConnectionError as e :
                if attemp < self._max_retries:
                    wait_time = 2**attemp
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type = EventType.ERROR,
                        error= f"Connection error happen { e }"
                    )
                    return

            except APIError as e:
                yield  StreamEvent(
                    type = EventType.ERROR,
                    error= f"API establishment fail { e }"
                )
                return



    async def _stream_response(
        self,
        client: AsyncOpenAI,
        kwargs: dict[str, Any]
        ) -> AsyncGenerator[StreamEvent, None]:

        response = await client.chat.completions.create(**kwargs)
        
        usage: TokenUsage | None = None
        finish_reason: str | None = None

        async for chunk in response:

            if hasattr (chunk, "usage") and chunk.usage:
                usage = TokenUsage(
                    prompt_tokens= chunk.usage.prompt_tokens,
                    completion_tokens= chunk.usage.completion_tokens,
                    total_tokens= chunk.usage.total_tokens,
                    cached_token= chunk.usage.prompt_tokens_details.cached_tokens
                )

            if not chunk.choices:
                continue
        
            choice = chunk.choices[0]
            delta  = choice.delta

            if choice.finish_reason:
                finish_reason  =choice.finish_reason
            
            if delta.content:
                yield StreamEvent(
                    type= EventType.TEXT_DELTA,
                    text_delta= TextDelta(delta.content)
                )

        yield StreamEvent(
            type= EventType.MESSAGE_COMPLETE,
            finish_reason=finish_reason,
            usage= usage,
        )

        

    async def _non_stream_response(
        self,
        client: AsyncOpenAI,
        kwargs: dict[str, Any],
    ) -> StreamEvent:
        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        text_delta = None
        if message.content:
            text_delta = TextDelta(content=message.content)

        usage = None
        if response.usage:
            usage = TokenUsage(
                prompt_tokens= response.usage.prompt_tokens,
                completion_tokens= response.usage.completion_tokens,
                total_tokens= response.usage.total_tokens,
                cached_token= response.usage.prompt_tokens_details.cached_tokens
            )

    
        return StreamEvent(
            type = EventType.MESSAGE_COMPLETE,
            text_delta= text_delta,
            finish_reason= choice.finish_reason,
            usage= usage
        )



