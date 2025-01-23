from flask_wtf.form import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired



class DogNumberForm(FlaskForm):
    number = IntegerField(
        validators=[
            DataRequired("이미지 파일을 불러주세요.")
        ]
    )
    submit = SubmitField("업로드")

class DetectorForm(FlaskForm):
    submit = SubmitField("감지")

class DeleteForm(FlaskForm):
    submit = SubmitField("삭제")

class UploadImageForm(FlaskForm):
    image = FileField(
        validators=[
        FileRequired("이미지 파일을 지정해 주세요."),
        FileAllowed(["png", "jpg", "jpeg"], "지원되지 않는 형식입니다.")
        ]
    )
    submit = SubmitField("업로드")