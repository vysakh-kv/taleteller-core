from pydoc import cli
from flask import Flask,request,send_file
from concurrent.futures import thread
from dotenv import dotenv_values
from text_to_speech import speak
from moviepy.editor import *
import requests,base64,yake,random,threading

app = Flask(__name__)

config = dotenv_values(".env")

def concatenate(clip_paths, id, method="compose"):

    clips = [VideoFileClip(c) for c in clip_paths]

    # clip = VideoFileClip()
    if method == "reduce":

        min_height = min([c.h for c in clips])
        min_width = min([c.w for c in clips])

        clips = [c.resize(newsize=(min_width, min_height)) for c in clips]
        final_clip = concatenate_videoclips(clips)
    elif method == "compose":
        final_clip = concatenate_videoclips(clips, method="compose")

    final_clip.write_videofile(f"{id}_merged.mp4")

def gen_clips(iprompt,numImg):
    data = {"text":iprompt,"num_images":numImg}
    try:
        print(f"Polling \"{iprompt}\"")
        r = requests.post(url = config["URL"], json = data)
        data = r.json()
        return data
    except:
        return None

def add_static_image_to_audio(image_path, audio_path, output_path):
    
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path)
    video_clip = image_clip.set_audio(audio_clip)

    video_clip.duration = audio_clip.duration
    video_clip.fps = 1
    video_clip.write_videofile(output_path)
    return


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
def merge():

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


# @app.route("/magic", methods=['POST'])
# def magic():
#     # Request ID Logic here
#     id = 'id'
#     if request.method=='POST':
#         v = request.json["prompt"], request.json["lang"], request.json["num"]
#         voice_prompts = v[0].split(".")
#         voice_prompts = [i for i in voice_prompts if i!='']
#         img_prompts = []

#         NUMPROMPT = v[1]
#         kw_extractor = yake.KeywordExtractor()

#         for i in range(NUMPROMPT):
#             keywords = kw_extractor.extract_keywords(voice_prompts[i])
#             img_prompts.append(keywords[0][0])

#         print("voice: \t",voice_prompts)
#         print("image: \t",img_prompts)


#         clips = []

#         threads = []
#         for i in range(NUMPROMPT):
#             x = threading.Thread(target=gen_clips, args=(img_prompts[i],2))
#             x.start()
#             threads.append(x)

#         voices = []
#         images = []
#         for i in range(NUMPROMPT):
#             t = threads[i].join()
#             t["data"]
#             clips.append(f"{i+1}.mp4")

#         concatenate(clips,"merged.mp4")