import json
import schedule
import time
import requests

client_id = ""
client_secret = ""

# define token dictionary as a variable
tokens = {
    "access_token": '',
    "refresh_token": ''
}

# Load tokens from the file
with open("/home/admin/apps/assistant/assistant/tokens.json", "r") as file:
    tokens = json.load(file)

# assign access token and refresh token
print('printing tokens before refresh')
access_token = tokens["access_token"]
print(access_token)
refresh_token = tokens["refresh_token"]
print(refresh_token)

def refreshToken(refresh_Token_in):
    url = "https://webexapis.com/v1/access_token"
    headers = {
        'accept':'application/json',
        # 'content-type':'application/x-www-form-urlencoded'
        }
    payload = {
        'grant_type': "refresh_token",
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_Token_in
        }

    response = requests.post(url=url, data=payload, headers=headers)
    results = response.json()
    # print(results)

    if response.status_code == 200:
        access_token = results["access_token"]
        refresh_token = results["refresh_token"]
        print("New Access Token: ", access_token)
        print("New Refresh Token: ", refresh_token)

         # Save tokens to a file
        with open("/home/admin/apps/assistant/assistant/tokens.json", "w") as file:
            json.dump(tokens, file)

    else:
        print("Request failed with status code:", response.status_code)
        print(response.text)  # Display the response body

refreshToken(refresh_token)
