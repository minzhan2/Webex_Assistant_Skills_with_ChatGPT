from webex_skills.api import SimpleAPI
from webex_skills.dialogue import responses
from webex_skills.models.mindmeld import DialogueState
import requests
import openai

api = SimpleAPI()

# Set parameters for the API request

openai.api_key = ""  # add your token here
model_engine = "text-davinci-003"
max_tokens = 50
temperature = 0.5

# all other questions routed to ChatGPT
@api.handle(default=True)
async def greet(current_state: DialogueState) -> DialogueState:

    new_state = current_state.copy()
    text = current_state.text

    if  text == "bye":
            new_state.directives = [
            responses.Reply("Thank you, good bye."),
            responses.Speak("Thank you, good bye."),
            responses.Sleep(10),
            ]

    else:
         # Generate a response from ChatGPT
        response = openai.Completion.create(
            engine=model_engine,
            prompt=text,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract the generated text from the response
        generated_text = response.choices[0].text.strip()
        # Print the generated text
        print("ChatGPT:", generated_text)
        new_state.directives = [
            responses.Reply(generated_text),
            responses.Speak(generated_text),
            responses.Listen(),
        ]

    return new_state





