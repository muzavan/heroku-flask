import os
import sys
import json
import time

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if message_text == "hi":
                        send_reply(sender_id)
                    elif message_text == "ha":
                        send_generic(sender_id)
                    elif message_text == "hu":
                        send_whitelist(recipient_id)
                    else:
                        send_message(sender_id, "roger that!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_whitelist(recipient_id):
    log("send whitelist")
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "whitelisted_domains" : ["https://petersfancyapparelx.com"],
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messenger_profile", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_reply(recipient_id):

    log("sending message to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text" : "This is a reply",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "Search",
                    "payload": "RED",
                    "image_url": "http://example.com/img/red.png"
                },
                {
                    "content_type": "location"
                },
            ]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_generic(recipient_id):

    log("sending message to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements":[
                   {
                    "title":"Welcome to Peter\'s Hats",
                    "subtitle":"This is subtitle",
                    "default_action": {
                      "type": "web_url",
                      "url": "https://www.facebook.com"
                    }
                  },
                    {
                        "title": "Welcome to Peter\'s Hats #2",
                        "subtitle": "This is subtitle",
                        "default_action": {
                            "type": "web_url",
                            "url": "https://petersfancyapparelx.com"
                        }
                    },
                    {
                        "title": "Welcome to Peter\'s Hats #3",
                        "subtitle": "This is subtitle",
                        "default_action": {
                            "type": "web_url",
                            "url": "https://petersfancyapparelx.com/page?v=wui"
                        }
                    },
                ]
              }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_sender_action(recipient_id):
    log("sending message to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action": "typing_on"
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    time.sleep(15)
    send_message(recipient_id,"This is after 15 seconds")


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
