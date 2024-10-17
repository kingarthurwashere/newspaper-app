from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Get credentials from environment variables
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WORDPRESS_API_URL = os.getenv("WORDPRESS_API_URL")

def send_whatsapp_message(recipient: str, message: str):
    """
    Sends a message using the WhatsApp Cloud API.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
    return response.status_code, response.json()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook to receive WhatsApp messages and respond.
    """
    data = await request.json()

    # Extract message details from the webhook payload
    phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    incoming_msg = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].strip().lower()

    if "news" in incoming_msg:
        # Fetch latest news from WordPress API
        response = requests.get(WORDPRESS_API_URL)
        if response.status_code == 200:
            posts = response.json()
            if posts:
                latest_post = posts[0]  # Get the most recent post
                title = latest_post['title']['rendered']
                link = latest_post['link']
                message = f"📰 Latest News: {title}\nRead more: {link}"
            else:
                message = "No news available at the moment."
        else:
            message = "Sorry, I couldn't fetch the news at the moment."
    else:
        message = "Send 'news' to get the latest articles."

    # Send the response back to the user via WhatsApp
    status_code, response = send_whatsapp_message(phone_number, message)
    return {"status": status_code, "response": response}

# Run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
