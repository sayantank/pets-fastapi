# Importing Libraries
import uvicorn

from fastapi import FastAPI, Request, UploadFile, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from fastai.vision.all import *

import os
import base64
import pathlib
import asyncio
import numpy as np
from PIL import Image
from io import BytesIO

from pydantic import BaseModel

# Initialising app and templating engine
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Adding static files to serve
app.mount("/static", StaticFiles(directory="static"), name="static")

# Declaring base path
try:
    path = Path(__file__).parent
except:
    path = Path(r'C:\\Users\\sayank\\workspace\\pets-fastapi\\')

model_name = 'pets_resnet18.pkl'

# Configuring CORS
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defining root route
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def load_posix_learner(path):
    save = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath
    
    learn = load_learner(path)
    
    pathlib.PosixPath = save
    return learn

async def setup_learner():
    try:
        print(path/model_name)
        try:
            learn = load_learner(path/model_name)
        except:
            learn = load_posix_learner(path/model_name)
        learn.dls.device = 'cpu'
        print("Loaded model")
        return learn
    except RuntimeError as e:
        print("lmao")
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

learn = None
@app.on_event("startup")
async def startup_event():
    """Setup the learner on server start"""
    global learn
    # loop = asyncio.get_event_loop()  # get event loop
    tasks = [asyncio.ensure_future(setup_learner())]  # assign some task
    learn = (await asyncio.gather(*tasks))[0]  # get tasks
    # learn = setup_learner()

class RequestBody(BaseModel):
    img_base64: str

@app.post("/upload")
async def create_file(req: RequestBody):
    try:
        if(req.img_base64[11:14] == "png"):
            img = req.img_base64.replace('data:image/png;base64,', '')
        else:
            img = req.img_base64.replace('data:image/jpeg;base64,', '')
        img = img.replace(' ', '+')
        img = base64.b64decode(img)
        img = Image.open(BytesIO(img)).convert('RGB')
        np_img = np.array(img)
        preds = learn.predict(np_img)
        print(preds)
    except:
        print("Prediction Failed")
        return {"pred": -1}
    return {"pred": preds[0]}