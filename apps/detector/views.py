import requests
import random
import cv2
import numpy as np
import torch
import torchvision
from pathlib import Path
from flask import Blueprint, render_template, current_app, send_from_directory, redirect, url_for, request, flash
from flask_login import current_user, login_required
from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag
from apps.detector.forms import DogNumberForm, DetectorForm
from flask_cors import CORS
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError


dt = Blueprint(
    "detector", 
    __name__, 
    template_folder="templates"
    )

@dt.route("/")
def index():
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )
    return render_template("detector/index.html", user_images=user_images)

@dt.route("/<filename>")
def image_file(filename):
    return filename[1:]

@dt.route("/upload", methods=["GET", "POST"])
@login_required
def upload_count():
    form = DogNumberForm()

    if form.validate_on_submit() :

        return redirect(url_for("detector.upload_image", number=form.number.data))

    return render_template("detector/upload.html", form=form)


@dt.route("/uploadimage/<number>", methods=["GET", "POST"])
def upload_image(number):
    
    url = f"https://dog.ceo/api/breeds/image/random/{number}"
    response = requests.get(url)

    if response.status_code == 200:
        # JSON 데이터 파싱
        data = response.json()
        print("데이터:", data)
        for img in data["message"] :
            user_image = UserImage(
                user_id = current_user.id,
                image_path= img
            )
            db.session.add(user_image)
            db.session.commit()
    else:
        print(f"요청 실패. 상태 코드: {response.status_code}")

    return redirect(url_for("detector.index"))

def make_color(labels) :
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color

def make_line(result_image) :
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line

def draw_lines(c1, c2, result_image, line, color) :
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2

def draw_texts(result_image, line, c1, cv2, color, labels, label) :
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA
    )
    return cv2

# 매개변수 : 물체 감지하라고 주어진 이미지의 경로
def exec_detect(target_image_path) :
    labels = current_app.config["LABELS"]
    image = Image.open(target_image_path)

    # 모델이 학습했던 유형의 데이터를 전달해줘야 예측도 가능
    # 텐서 : 다차원 배열
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    model = model.eval()
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())
    for box, label, score in zip(
        output["boxes"], output["labels"], output["scores"]
    ):
        # 점수가 0.5점 이상이고 신규 발견된 라벨이라면
        if score > 0.5 and labels[label] not in tags :
            color = make_color(labels)
            line = make_line(result_image)
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))

            cv2 = draw_lines(c1, c2, result_image, line, color)
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])

    detected_image_file_name = str(uuid.uuid4()) + ".jpg"
    detected_image_file_path = str(Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name))

    cv2.imwrite(detected_image_file_path, cv2.cvtColor(
        result_image, cv2.COLOR_RGB2BGR
    ))
    return tags, detected_image_file_name

def save_detected_image_tags(user_image, tags, detected_image_file_name):
    user_image.image_path = detected_image_file_name
    user_image.is_detected = True
    db.session.add(user_image) # primary key 가 같은 레코드를 삽입하면 업데이트

    for tag in tags :
        user_image_tag = UserImageTag(
            user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)

    db.session.commit()

@dt.route("/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None :
        flash("물체 감지 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.index"))
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"], user_image.image_path
    )

    tags, detected_image_file_name = exec_detect(target_image_path)
    try:
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생했습니다.")
        db.session.rollback()
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))
    return redirect(url_for("detector.index"))