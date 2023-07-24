# the codes below are for demo only, it does not include error handling mechanism.
# The codes below works for my desk pro, some minor changes might be required to work on other devices.

from webex_skills.api import SimpleAPI
from webex_skills.dialogue import responses
from webex_skills.models.mindmeld import DialogueState
import requests
import openai
import json
import schedule
import time

api = SimpleAPI()
openai.api_key = ""  # add your token here


# Set some parameters for OpenAI access
model_engine = "text-davinci-003"
max_tokens = 50
temperature = 0.5

# add Webex Control Hub access token here, or codes here to get and refresh tokens
access_token = ''

def askTemperature(deviceId):
    base_url = "https://webexapis.com/v1/xapi/status"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "deviceId": deviceId,
        "name": "RoomAnalytics.AmbientTemperature",
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data["result"]["RoomAnalytics"]["AmbientTemperature"]

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def askPeopleCount(deviceId):
    base_url = "https://webexapis.com/v1/xapi/status"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "deviceId": deviceId,
        "name": "RoomAnalytics.PeopleCount.Current",
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data["result"]["RoomAnalytics"]["PeopleCount"]["Current"]
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# turn on 3D Map of the floor
@api.handle(pattern=r'.*\smap\s?.*')
async def map_on(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()

    text = 'Ok, turning on the 3D Map.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        # specify the URL to be displayed by device
        responses.DisplayWebView("https://workspaces.dnaspaces.io/#/preview/?token=22409a46-c506-4e72-b3a2-79615b7a8973", "3D Map"),
        responses.Sleep(10),
    ]

    return new_state


# turn on music
@api.handle(pattern=r'.*\smusic\s?.*')
async def music_on(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()
    text = 'Ok, music is on your way.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        # specify the URL to be displayed by device
        responses.DisplayWebView("https://www.youtube.com/embed/TE9C1WrCIjA?autoplay=1", "2023 Top Songs"),
        responses.Sleep(10),
    ]

    return new_state

# turn off map or music
@api.handle(pattern=r'.*\soff\s?.*')
async def webview_off(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()

    text = 'Ok, turning off.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        responses.ClearWebView(),
        responses.Sleep(10),
    ]

    return new_state


# ask about the room temperature
@api.handle(pattern=r'.*\stemperature\s?.*')
async def TemperatureQuery(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()

    # use two lines of code below to understand the data structure
    # state_attributes = vars(current_state)
    # print(state_attributes)

    # Get DeviceId first
    current_state_json = current_state.json()
    current_state_dict = json.loads(current_state_json)
    DeviceId = current_state_dict["context"]["developerDeviceId"]
    print(DeviceId)

    # use xAPI to retrieve the temperature of the room
    Temp = askTemperature(DeviceId)
    print(Temp)

    text = f'Current temperature in the room is {Temp} degree, it is comfortable for a meeting!'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        responses.Sleep(10),
    ]

    return new_state

# ask about how many people in the room
@api.handle(pattern=r'.*\speople\s?.*')
async def PeopleCount(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()
    # Get DeviceId first
    current_state_json = current_state.json()
    current_state_dict = json.loads(current_state_json)
    DeviceId = current_state_dict["context"]["developerDeviceId"]
    print(DeviceId)

    PeopleNumber = askPeopleCount(DeviceId)
    text = f'Sure, there are {PeopleNumber} people in the room.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        responses.Sleep(10),
    ]

    return new_state

# all other questions routed to ChatGPT
@api.handle(default=True)
async def greet(current_state: DialogueState) -> DialogueState:

    new_state = current_state.copy()
    # Concatenate the prompt and the user's input

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

