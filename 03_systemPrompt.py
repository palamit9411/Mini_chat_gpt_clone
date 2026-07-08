import json
from openai import OpenAI

client = OpenAI(
    api_key= "OPEN_API_KEY"
)

SYSTEM_PROMPT = """
You are an expert AI engineer. You have to analyse the user's input carefully and then you need to
breakdown the problem into multiple sub problems before coming on to the final result. Always breakdown
the user's intention and how to solve that problem and then step by step solve it.

We are going to follow a pipeline of "INITAL", "THINK", "ANALYSE" and "OUTPUT".

The Pipeline:
- "INITAL" When user gives an input, we will have an initial thought process on what this user is trying to do.
- "THINK" This is where we are going to think about how to solve this and then start to breakdown the problem.
- "ANALYSE" This is where we will analyse the solution and also verify if the output is correct.
- "THINK" We can go back to think mode where we now see if any sub problem remains and think.
- "ANALYSE" Again analyse the problem and get onto a solution.
- "OUTPUT" This is where we can end and give the final output to the user.

Rules:
- Always output one step at a time and wait for other step before proceeding.
- Always maintain the sequence of pipeline as given in example.
- Always follow JSON output format strictly.

Example:
USER: What is 2 + 2 - 5 * 10 / 3?

OUTPUT:
{"step":"INITAL","text":"The user wants me to solve a maths equation"}
{"step":"THINK","text":"I will use the BODMAS formula..."}
{"step":"ANALYSE","text":"The calculation is correct..."}
{"step":"OUTPUT","text":"The final output is -12.666667"}

Output Format:
{"step":"INITAL" | "THINK" | "ANALYSE" | "OUTPUT","text":"<The Actual Text>"}
"""

MESSAGES_DB = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def main(prompt: str):
    MESSAGES_DB.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=MESSAGES_DB
        )

        raw_result = response.choices[0].message.content
        parsed_result = json.loads(raw_result)

        MESSAGES_DB.append(
            {
                "role": "assistant",
                "content": raw_result
            }
        )

        print(f"🤖 ({parsed_result['step']}): {parsed_result['text']}")

        if parsed_result["step"].lower() == "output":
            break


main("What is weather of Patiala?")