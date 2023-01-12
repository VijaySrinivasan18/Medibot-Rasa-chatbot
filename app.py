import os
from flask import Flask,render_template,request,jsonify
from werkzeug.utils import secure_filename
import  PIL.Image as Image 
import io
import base64
import requests




app=Flask("__name__")
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),"temp_imgs")

@app.get("/")
def index_get():
    requests.post(r"http://localhost:5002/webhooks/rest/webhook",json={"message":"/restart"})
    return render_template("base.html")

@app.post("/predict")
def predict():
    text=request.get_json().get("message")
    # response= get_response(text)
    response= requests.post(r"http://localhost:5002/webhooks/rest/webhook",json={"message":text})
    resp=""
    if len(response.json())==0:
        return jsonify({"answer":"I am sorry, I can't understand.Could you please rephrase your query"})

    for i in response.json():
        if "text" in i.keys():
            print("raw_reply",i["text"])
            resp=resp+i["text"]+" "
        elif "image" in i.keys():
            print(i["image"])
            return jsonify({"answer":"Image"})

    try:
        message={"answer":resp}
    except UnboundLocalError as e:
        return jsonify({"answer":"I am sorry, I can't understand.Could you please rephrase your query"})
    return jsonify(message)

@app.post("/img")
def img_upload():
    text=request.get_json().get("message")
    if text[5:10].split("/")[0]!="image":
        return jsonify({"answer":"It is not a valid image file. Please enter an image file"})
    else:
        text=text[text.find("base64,")+len("base64,"):]
        text=bytes(text,encoding="utf-8")
        b=base64.b64decode(text)
        img=Image.open(io.BytesIO(b))
        img.save("temp_imgs/trial_img.png")
        message={"answer":"Image received"}
        return jsonify(message)



    


if __name__=="__main__":
    app.run(debug=True)