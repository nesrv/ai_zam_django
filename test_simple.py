import requests

TOKEN = "7836693206:AAFgvbLhQSuDCCWPr5zaafDn0W_-CGF0yGk"

print("Testing bot token...")
url = f'https://api.telegram.org/bot{TOKEN}/getMe'
response = requests.get(url)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("Token is VALID")
else:
    print("Token is INVALID")
    print("Possible reasons:")
    print("1. Bot was deleted")
    print("2. Token is wrong")
    print("3. Network issues")