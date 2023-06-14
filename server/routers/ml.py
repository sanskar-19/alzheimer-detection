from fastapi import (
    APIRouter,
    Header,
    status,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form,
)
from ..schema import user as user_schema
from ..utils import db, exceptions, jwt as jwt_utils, user as user_utils
from ..models.user import UserModel
from sqlalchemy.orm import Session
from ..database import get_db
from pydantic import EmailStr
from datetime import datetime, timedelta
from ..schema import alzheimer
from config import setting

import os
import urllib.request

from werkzeug.utils import secure_filename
import cv2
import pickle
import imutils
import sklearn
from keras.models import load_model
import numpy
import shutil

# from pushbullet import PushBullet
import joblib
import numpy as np
from keras.applications.vgg16 import preprocess_input

db = get_db()
router = APIRouter(prefix="/api/ml")
alzheimer_model = load_model("server/utils/ml/models/alzheimer_model.h5")
alzheimer_model_v2 = load_model("server/utils/ml/models/alzheimer_model_v2.h5")

categories = ["NonDemented", "MildDemented", "ModerateDemented", "VeryMildDemented"]
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


# Utility functions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

# Adding route for ml v2
@router.post("/alzheimer-detect-v2")
async def alzheimer_detect(
    first_name: str, last_name: str, age: int, contact: str, scan: UploadFile
):
    if scan and allowed_file(scan.filename):
        filename = secure_filename(scan.filename)
        with open(setting.UPLOAD_FOLDER + "/" + filename, "wb") as buffer:
            shutil.copyfileobj(scan.file, buffer)
        # file.save(os.path.join(setting.UPLOAD_FOLDER, filename))
        # flash("Image successfully uploaded and displayed below")
        img = cv2.imread(setting.UPLOAD_FOLDER + "/" + filename)
        img = cv2.resize(img, (176, 176))
        img = img.reshape(1, 176, 176, 3)
        img = img / 255.0
        pred = alzheimer_model.predict(img)
        pred = pred[0].argmax()
        print(pred)
        return {
            "data": {
                "results": exceptions.findCondition(filename, pred),
                "patient": {
                    "Name": first_name + " " + last_name,
                    "Age": age,
                    "Contact": contact,
                },
            },
            "message": "Details Fetched Successfully",
        }
    else:
        return "Allowed image types are - png, jpg, jpeg"


# Adding route for ml v1
@router.post("/alzheimer-detect-v1")
async def alzheimer_detect(
    first_name: str, last_name: str, age: int, contact: str, scan: UploadFile
):
    if scan and allowed_file(scan.filename):
        filename = secure_filename(scan.filename)
        with open(setting.UPLOAD_FOLDER + "/" + filename, "wb") as buffer:
            shutil.copyfileobj(scan.file, buffer)
        # file.save(os.path.join(setting.UPLOAD_FOLDER, filename))
        # flash("Image successfully uploaded and displayed below")
        img = cv2.imread(setting.UPLOAD_FOLDER + "/" + filename)
        img = cv2.resize(img, (176, 176))
        img = img.reshape(1, 176, 176, 3)
        img = img / 255.0
        pred = alzheimer_model.predict(img)
        pred = pred[0].argmax()
        print(pred)
        return {
            "data": {
                "results": None,
                "patient": {
                    "Name": first_name + " " + last_name,
                    "Age": age,
                    "Contact": contact,
                },
            },
            "message": "Details Fetched Successfully",
        }
    else:
        return "Allowed image types are - png, jpg, jpeg"
    


# Adding route for ml v2
@router.post("/alzheimer-detect-v0")
async def alzheimer_detect(file: UploadFile):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        with open(setting.UPLOAD_FOLDER + "/" + filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # file.save(os.path.join(setting.UPLOAD_FOLDER, filename))
        # flash("Image successfully uploaded and displayed below")
        img = cv2.imread(setting.UPLOAD_FOLDER + "/" + filename)
        img = cv2.resize(img, (120, 120))
        img = numpy.array(img).reshape(-1, 120, 120, 1)
        img = img / 255.0
        pred = alzheimer_model_v2.predict(img)
        # ptitle = "Prediction: {0}".format(categories[np.argmax(pred)])
        pred = pred[0].argmax()
        # print(ptitle)
        return {"data": str(pred)}
    else:
        return "Allowed image types are - png, jpg, jpeg"
