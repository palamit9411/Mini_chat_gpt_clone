from openai import OpenAI
import json
import requests
import subprocess

client = OpenAI(
    api_key= "OPEN_API_KEY"
)

def get_weather_data(city_name):
    url = f"https://wttr.in/{city_name.lower()}?format=%C+%t"

    response = requests.get(url)

    return json.dumps({
        "cityName": city_name,
        "weatherInfo": response.text
    })


def execute_command_on_cli(cmd):
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True
        )

        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })

    except Exception as e:
        return json.dumps({
            "error": str(e)
        })

SYSTEM_PROMPT ="""
  You are an expert AI engineer. Only and only answer questions related to the coding and enginnering.
  
  Persona: You are a senior software developer.
  Persona Traits:
  - You always sound techical and use jargons.
  - You never answer back on personal things and you don't have a personal life
  - All you know is how and what code is

  You have to analyse the user's input carefully and then you need to
  breakdown the problem into multiple sub problems before comming on to the final result. Always breakdown
  the users intention and how to solve that problem and then step by step solve it.

  We are going to follow a pipeline of "INITAL", "THINK", "TOOL_REQUEST", "ANALYSE" and "OUTPUT" pipline.

  The Pipeline:
  - "INITAL" When user gives an input, we will have an inital thought process on what this user is trying to do.
  - "THINK" this is where we are going to think about how to solve this and then start to breakdown the problem
  - "ANALYSE" this is where we will analyse the solution and also verify if the output is correct
  - "THINK" we can go back to think mode where we now see if any sub problem remanins and think
  - "ANALYSE" again analyse the problem and get onto a solution
  - "TOOL_REQUEST": use this for calling or requesting a tool. The format of output would be
    { "step": "TOOL_REQUEST", functionName: "getWeatherData", "input": "Goa" }
  - "OUTPUT" this is where we can end and give the final output to the user.

  Available Tools:
  - "getWeatherData": getWeatherData(cityName: string): Returns the realtime weather information of city
  - "executeCommandOnCli": executeCommandOnCli(command: string): Executes the command on user's device and returns output from stdout

  Environment:
- The user's operating system is Windows.
- The terminal is Windows PowerShell.
- Whenever you generate CLI commands, ALWAYS generate Windows PowerShell compatible commands.
- Never generate Linux or macOS commands.
- Do not use commands like touch, ls, pwd, cat, rm -rf, chmod.
- Instead use PowerShell commands like:
    - New-Item
    - New-Item -ItemType Directory
    - Get-ChildItem
    - Set-Content
    - Remove-Item
    - Start-Process

  Rules:
  - Always output one step at a time and wait for other step before proceeding.
  - Always maintain the sequence of pipeline as given in example
  - Always follow JSON output format strictly.

  Example:
  - "USER": What is 2 + 2 - 5 * 10 / 3?
  OUTPUT:
  - "INITAL": "The user wants me to solve a maths equation"
  - "THINK": "I will use the BODMAS formula and based on that I should firt multiple 5 * 10 which is 50"
  - "ANALYSE": "Yes, the bodmas is actaully right and now equation is 2 + 2 - 50 / 3"
  - "THINK": "Now as per rule I should perform divide which is dividing 50 / 3 which is 16.666667"
  - "ANALYSE": "Now the new equations remains 2 + 2 - 16.666667"
  - "THINK": "Now its simple we can just do 2 + 2 = 4 and new equation remains 4 - 16.6666667"
  - "ANALYSE": "Great, now lets just do the final step as simple subtraction"
  - "THINK": "After the final subtraction the ans remations -12.666667"
  - "OUTPUT": "The final output is "-12.666667"

  Example:
  - "USER" what is weather of Goa?
  OUTPUT:
   - "INITAL": "The user wants me to fetch weather information of Goa",
   - "THINK": "From the tools I can see we have a tool named getWeatherData which can be called"
   - "ANALYSE": "We are going right we can call getWeatherData with "GOA" as input"
   - "TOOL_REQUEST": { "functionName": "getWeatherData", "input": "goa" }
   - "TOOL_OUTPUT": The weather of Goa is sunny with some 30 degree c.
   - "THINK": "We got the weather info"
   - "OUTPUT": "The weather of Goa is sunny with some 30 degree c. Its goona be Hottttttt"

  Output Format:
  { "step": "INITAL" | "THINK" | "TOOL_REQUEST |"ANALYSE" | "OUTPUT", "text": "<The Actual Text>", "functionName": "<NAME OF FUNCTION>", "input": "INPUT PARAMS of Function" }

"""

MESSAGES_DB = [

    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


def main(prompt=""):
    MESSAGES_DB.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    while True:

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=MESSAGES_DB
            )

            raw_result = response.choices[0].message.content

            try:
                parsed_result = json.loads(raw_result)
            except json.JSONDecodeError:
                print("❌ Model did not return valid JSON")
                print(raw_result)
                break

            MESSAGES_DB.append(
                {
                    "role": "assistant",
                    "content": raw_result
                }
            )

            # -----------------------------
            # Print safely
            # -----------------------------
            step = parsed_result.get("step", "").upper()

            if step == "TOOL_REQUEST":
                print(
                    f"🛠️ TOOL_REQUEST -> {parsed_result.get('functionName')}({parsed_result.get('input')})"
                )
            else:
                print(
                    f"🤖 ({step}): {parsed_result.get('text', '')}"
                )

            # -----------------------------
            # Stop if OUTPUT
            # -----------------------------
            if step == "OUTPUT":
                break

            # -----------------------------
            # Execute Tool
            # -----------------------------
            if step == "TOOL_REQUEST":

                function_name = parsed_result.get("functionName")
                tool_input = parsed_result.get("input")

                if function_name == "executeCommandOnCli":

                    tool_result = execute_command_on_cli(tool_input)

                    print(f"🛠️ Executing: {tool_input}")
                    print(tool_result)

                    MESSAGES_DB.append(
                        {
                            "role": "system",
                            "content": json.dumps({
                                "step": "TOOL_OUTPUT",
                                "output": tool_result
                            })
                        }
                    )

                    continue

                elif function_name == "getWeatherData":

                    tool_result = get_weather_data(tool_input)

                    print(f"🌤️ Weather Tool: {tool_input}")
                    print(tool_result)

                    MESSAGES_DB.append(
                        {
                            "role": "system",
                            "content": json.dumps({
                                "step": "TOOL_OUTPUT",
                                "output": tool_result
                            })
                        }
                    )

                    continue

                else:
                    print(f"❌ Unknown Tool: {function_name}")
                    break

        except Exception as e:
            print("❌ Error:", e)
            break

main(
    "Build a funny functional design working TODO application and run on browser and store all files on todo folder"
)
           