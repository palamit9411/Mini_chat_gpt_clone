from openai import OpenAI

client = OpenAI(
    api_key= "OPEN_API_KEY"
)

def api_function(client):

    response = client.responses.create(
        model="gpt-4o-mini",
        input="""
    What is 2 + 5 equals?

    Do not add anything else in the answer. Take the samples from the examples.

    Examples:
    - What is 5 + 4?
    Expected Output: 9 (Nine)

    - What is 10 + 10?
    Expected Output: 20 (Twenty)
    """
    )

    print("Ans from OpenAI API:", response.output_text)

api_function(client)