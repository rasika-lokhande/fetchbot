from openai import OpenAI
from pydantic import BaseModel
from system_prompt import SYSTEM_PROMPT

client = OpenAI()

user_prompt = "Take yellow bottle to the kitchen"

class SearchCommand(BaseModel):
    target_object: str
    source: str
    destination: str

response = client.responses.parse(
    model="gpt-4o-mini-2024-07-18",
    input=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    text_format=SearchCommand,
)

parsed_command = response.output_parsed

print(parsed_command)

