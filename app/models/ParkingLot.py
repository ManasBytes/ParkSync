from app.extensions import db
from sqlalchemy import func

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column (db.String(100), nullable = False)
    total_spots = db.Column(db.Integer, nullable = False)
    price_per_hour = db.Column(db.Float, nullable = False)
    created_at = db.Column (db.DateTime, server_default = func.now())
    
    
    spots = db.relationship('ParkingSpot', backref = 'lot', lazy = True, cascade = 'all, delete-orphan')
    
    def get_available_spots_count(self):
        return sum(1 for spot in self.spots if not spot.is_booked)
    
    def get_booked_spots_count(self):
        return sum(1 for spot in self.spots if spot.is_booked)
    
    def __repr__(self):
        return f'<ParkingLot {self.name}>'
    
    
    
    
    