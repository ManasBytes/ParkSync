from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ParkingLotForm(FlaskForm):
    name = StringField('Parking Lot Name', validators=[DataRequired()])
    total_spots = IntegerField('Total Spots', validators=[DataRequired(), NumberRange(min=1, max=500)])
    price_per_hour = FloatField('Price Per Hour ($)', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Add Parking Lot')

class UpdateSpotsForm(FlaskForm):
    total_spots = IntegerField('Total Spots', validators=[DataRequired(), NumberRange(min=1, max=500)])
    submit = SubmitField('Update Spots')