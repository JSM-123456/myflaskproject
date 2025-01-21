from flask_wtf.form import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class DogNumberForm(FlaskForm):
    number = IntegerField(
        validators=[
            DataRequired("이미지 파일을 불러주세요.")
        ]
    )
    submit = SubmitField("업로드")

class DetectorForm(FlaskForm):
    submit = SubmitField("감지")