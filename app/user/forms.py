from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class BookingForm(FlaskForm):
    spot_id = HiddenField('Spot ID', validators=[DataRequired()])
    vehicle_number = StringField('Vehicle Number', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Book Spot')