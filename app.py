from pydoc import cli
from flask import Flask,request,send_file
from dotenv import dotenv_values
from text_to_speech import speak
from moviepy.editor import *
import requests,base64,yake,random,threading

app = Flask(__name__)

config = dotenv_values(".env")

def gen_clips(iprompt,numImg):
    data = {"text":iprompt,"num_images":numImg}
    try:
        print(f"Polling \"{iprompt}\"")
        r = requests.post(url = config["URL"], json = data)
        data = r.json()
        return data
    except:
        return None

@app.route("/dalle", methods=['POST'])
def dalle_img():

    # print(request.json)
    data = gen_clips(request.json["prompt"],request.json["num"])
    return {
        "data": data,
        "error": "dalle backend not running!",
    }

