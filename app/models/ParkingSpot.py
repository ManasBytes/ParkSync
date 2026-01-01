from app.extensions import db

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    spot_number = db.Column(db.Integer, nullable = False)
    
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    
    is_booked = db.Column(db.Boolean, nullable = False, default = False)
    
    reservation = db.relationship('Reservation', backref = 'spot' , lazy = True)
    
    def __repr__(self):
        return f'<Spot {self.spot_number} in lot {self.lot_id}>'
    
    