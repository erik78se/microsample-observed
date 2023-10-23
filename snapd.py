import requests
import requests_unixsocket

# Define the Unix domain socket path
snapd_socket = "/run/snapd.socket"

# Define the snapd API endpoint
snapd_url = "http+unix://%2Frun%2Fsnapd.socket/v2/apps"


session = requests_unixsocket.Session()

# Use the requests library to send a GET request over the Unix domain socket
response = session.get(snapd_url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Failed to retrieve Snap apps. Status code: {response.status_code}")



