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

@app.route("/tts", methods=['GET','POST'])
def tts():
    # Request ID Logic here
    id = 'id'
    if request.method=='POST':
        v = request.json["prompt"], request.json["lang"]
        speak(v[0], v[1], save=True, file=f"{id}.mp3", speak=False)
        return send_file(
            f"{id}.mp3", 
            mimetype="audio/mpeg", 
            as_attachment=True)


@app.route("/merge", methods=['POST'])
def merge():​
# Request ID Logic here
    id = 'id'
    if request.method=='POST':
    images = request.files.getlist("images")
    audios = request.files.getlist("audio")

    N = len(images)
    clips = []
    print(images)
    print(audios)
    for i in range(N):

    f = open(f"{images[i].filename}","wb")
    images[i].save(f)
    f.close()
    f = open(f"{audios[i].filename}","wb")
    audios[i].save(f)
    f.close()

    add_static_image_to_audio(images[i].filename,audios[i].filename,f"{id}_{images[i].filename}.mp4")
    clips.append(f"{id}_{images[i].filename}.mp4")
    concatenate(clips,id)
    return send_file(
    f"{id}_merged.mp4", 
    mimetype="video/mp4", 
    as_attachment=True)


@app.route("/merge/b64", methods=['POST'])
def mergeb64():

    # Request ID Logic here
    id = 'id'
    if request.method=='POST':
        images = request.json["images"]
        audios = request.json["audio"]
        afmt = request.json["audiofmt"]
        ifmt = request.json["imgfmt"]

        N = len(images)
        clips = []
        for i in range(N):
            f = open(f"{id}_{i}.{ifmt}", "wb")
            f.write(base64.b64decode(images[i]))
            f.close()
            f = open(f"{id}_{i}.{afmt}", "wb")
            f.write(base64.b64decode(audios[i]))
            f.close()
            add_static_image_to_audio(f"{id}_{i}.{ifmt}",f"{id}_{i}.{afmt}",f"{id}_{i}.mp4")
            clips.append(f"{id}_{i}.mp4")
        concatenate(clips,id)
        return send_file(
            f"{id}_merged.mp4", 
            mimetype="video/mp4", 
            as_attachment=True)