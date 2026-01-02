from app.extensions import db
from sqlalchemy import func
class Payment(db.Model):
    id= db.Column(db.Integer, primary_key = True, autoincrement = True)
    reservation_id  = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable = False)
    amount = db.Column(db.Float, nullable =  False)
    is_paid = db.Column (db.Boolean, nullable = False, default = False)
    payment_date = db.Column(db.DateTime, nullable = True)
    created_at = db.Column(db.DateTime, server_default = func.now())
    
    def __repr__(self):
        return f'<Payment {self.id} - amount {self.amount} Status {self.is_paid}>'