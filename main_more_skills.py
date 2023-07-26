# the codes below are for demo only, it does not include error handling mechanism.
# Last modified on July 26th, 2023

from webex_skills.api import SimpleAPI
from webex_skills.dialogue import responses
from webex_skills.models.mindmeld import DialogueState
import requests
import openai
import json


api = SimpleAPI()
# add your openAI token here
openai.api_key = ""

# Set parameters for the API request
model_engine = "text-davinci-003"
max_tokens = 50
temperature = 0.5

# Access Token for xAPI - Webex Control Hub
access_token = ''

# retrieve access token stored in a local file named "tokens.json"
def getToken():
    # Load tokens from the file
    tokens = {
    "access_token": '',
    "refresh_token": ''
    }

    with open("/home/admin/apps/assistant/assistant/tokens.json", "r") as file:
        tokens = json.load(file)

    # assign access token and refresh token
    global access_token
    access_token = tokens["access_token"]


# run getToken once everytime the service is restarted 
# restart the assistant service every day in the night to refresh the token for xAPI
getToken()
print('current access token:' + access_token)


# IoT sensor APIs are different between Board & Desk series and Room Series
# Check device type
def CheckDeviceType(deviceId):
    base_url = f"https://webexapis.com/v1/devices/{deviceId}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url=base_url, headers=headers)
        response.raise_for_status()
        ProductType_Data = response.json()
        ProductType = ProductType_Data["product"].lower()

        # Check if "desk" or "board" is present in the ProductType
        if "desk" in ProductType or "board" in ProductType:
            print('Device type is Desk or Board')
            return True
        else:
            print('Device type is Room Series')
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# use xAPIs to get temeperature info for the room
def askTemperature(deviceId, isDeskorBoard):
    base_url = "https://webexapis.com/v1/xapi/status"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    if (isDeskorBoard):
        params = {
            "deviceId": deviceId,
            "name": "RoomAnalytics.AmbientTemperature", }
    else:
        params = {
            "deviceId": deviceId,
            "name": "Peripherals.ConnectedDevice[1001].RoomAnalytics.AmbientTemperature"}

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print("Response retrieved from Control Hub:")
        print(data)

        if (isDeskorBoard):
            return data["result"]["RoomAnalytics"]["AmbientTemperature"]
        else:
            return data["result"]["Peripherals"]["ConnectedDevice"][0]["RoomAnalytics"]["AmbientTemperature"]

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# use xAPI to get people count info for the room
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
        # 1. Create `display-web-view` directive and include payload
        responses.DisplayWebView(
            "https://workspaces.dnaspaces.io/#/preview/?token=22409a46-c506-4e72-b3a2-79615b7a8973", "3D Map"),
        responses.Listen()
    ]

    return new_state


# turn on music
@api.handle(pattern=r'.*\smusic\s?.*')
async def map_on(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()
    text = 'Ok, music is on your way.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        # 1. Create `display-web-view` directive and include payload
        responses.DisplayWebView(
            "https://www.youtube.com/embed/TE9C1WrCIjA?autoplay=1", "2023 Top Songs"),
        responses.Listen()
    ]

    return new_state

# turn off map or music
@api.handle(pattern=r'.*\soff\s?.*')
async def map_off(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()

    text = 'Ok, turning off.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        # 2. Create `clear-web-view` directive
        responses.ClearWebView(),
        responses.Listen()
    ]

    return new_state


# ask about the room temperature
@api.handle(pattern=r'.*\stemperature\s?.*')
async def map_on(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()

    # unquote two line below to understand the data structure
    # state_attributes = vars(current_state)
    # print(state_attributes)

    # Get DeviceId from Query first
    current_state_json = current_state.json()
    current_state_dict = json.loads(current_state_json)
    DeviceId = current_state_dict["context"]["developerDeviceId"]
    print("Get DeviceId: " + DeviceId)
    print("Start to check temperature for this device." )

    # check device type, different device type have their own APIs
    isDeskorBoard = CheckDeviceType(DeviceId)

    # check temperature based on device ID and device type
    Temp = askTemperature(DeviceId, isDeskorBoard)
    print("Current Temperature in the room is: " + Temp + "degree")

    text = f'Current temperature in the room is {Temp} degree, it is comfortable for a meeting!'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        #responses.Sleep(10),
        responses.Listen()
    ]

    return new_state

# ask about how many people in the room
@api.handle(pattern=r'.*\speople\s?.*')
async def map_on(current_state: DialogueState) -> DialogueState:
    new_state = current_state.copy()
    # Get DeviceId from Query first
    current_state_json = current_state.json()
    current_state_dict = json.loads(current_state_json)
    DeviceId = current_state_dict["context"]["developerDeviceId"]
    print("Get DeviceId: " + DeviceId)
    print("Start to check People Count for this room." )    


    PeopleNumber = askPeopleCount(DeviceId)
    print(f"There are {PeopleNumber} people in the room.")    
    text = f'Sure, there are {PeopleNumber} people in the room.'

    new_state.directives = [
        responses.Reply(text),
        responses.Speak(text),
        #responses.Sleep(10),
        responses.Listen()
    ]

    return new_state

# all other questions routed to ChatGPT

@api.handle(default=True)
async def greet(current_state: DialogueState) -> DialogueState:

    new_state = current_state.copy()
    # Concatenate the prompt and the user's input

    text = current_state.text

    if text == "bye":
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
            responses.Listen()
        ]

    return new_state


