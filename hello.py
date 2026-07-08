from openai import OpenAI
client = OpenAI(
    api_key= "OPEN_API_KEY"
)

response = client.responses.create(
    model="gpt-4",
    input="Hello, How are you?"
)

print(response.output_text)