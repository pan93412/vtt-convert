import asyncio
import itertools
import json
from typing import Coroutine, cast

import aiofiles
import openai

def chunk_vtt(content: str, size: int = 10):
    chunks = content.split("\n\n")
    return [chunks[pos:pos + size] for pos in range(0, len(chunks), size)]


async def translate_and_correct(client: openai.AsyncClient, chunk: list[str]):
    content = "\n\n".join(chunk)
    prompt = """You are a professional proofreader for a subtitle file. This is the transcript of a data analysis final report. You should translate it into Chinese (Traditional) in Taiwan terms, and correct all the typos and punctuation errors. You don't correct the content itself, just the typos and punctuation errors."""

    content = f"""Original:
{content}

Translation:
"""

    response = await client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.3,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "translation",
                "description": "The translation and correction of the subtitle file.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "translation": {"type": "string"}
                    },
                    "required": ["translation"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    )

    content = response.choices[0].message.content
    if content is None:
        return "<!翻譯失敗!>"

    return cast(str, json.loads(content)["translation"])


async def main() -> None:
    async with aiofiles.open("example.vtt", "r") as f:
        content = await f.read()

    chunks = chunk_vtt(content)
    print(chunks)

    results: list[Coroutine[None, None, tuple[int, str]]] = []
    semaphore = asyncio.Semaphore(4)

    async with openai.AsyncClient() as client:
        for index, chunk in enumerate(chunks):
            async def task(index: int, chunk: list[str]):
                print("Processing chunk", index)
                async with semaphore:
                    result = await translate_and_correct(client, chunk)
                print("Processed chunk", index)
                return index, result

            results.append(task(index, chunk))

        results_done = await asyncio.gather(*results)

    async with aiofiles.open("example_zh-TW.vtt", "w") as f:
        for index, result in sorted(results_done, key=lambda x: x[0]):
            print("Writing chunk", index)
            await f.write(result + "\n\n")


if __name__ == "__main__":
    asyncio.run(main())

