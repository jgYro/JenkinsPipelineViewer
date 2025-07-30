import requests


params = {
    "limit": "1000",
}

response = requests.get(
    "http://localhost:8080/blue/rest/organizations/jenkins/pipelines/CC2/runs/4/nodes/",
    params=params,
    auth=("Yro", "9106c1c8ffb9ca0ca3c5ee102791df0d"),
)

# Extract displayName for each object
display_names = [
    node.get("displayName") for node in response.json() if "displayName" in node
]

# Output the results
for name in display_names:
    print(name)
