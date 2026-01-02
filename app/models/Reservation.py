from app.extensions import db
from sqlalchemy import func
from .ParkingSpot import ParkingSpot
from datetime import datetime



class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key = True , autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete='SET NULL'), nullable=True)
    vehicle_number = db.Column(db.String(20), nullable = False)
    
    
    start_time = db.Column(db.DateTime, nullable = False, server_default = func.now())
    end_time = db.Column(db.DateTime, nullable = True)
    is_active = db.Column(db.Boolean, nullable = False, default = False)
    
    
    #snapshots
    lot_name_snapshot  = db.Column(db.String(100))
    spot_number_snapshot = db.Column(db.Integer)
    price_per_hour_snapshot = db.Column(db.Float)
    
    
    #this is required to store the history of spots or lots of parking for, if a lot is deleted, the balance or the amount #earned must not be deleted
    
    payment = db.relationship('Payment', backref = 'reservation', uselist = False, cascade = 'all, delete-orphan')
    
    
    def calculate_duration_hours(self):
        end = self.end_time or datetime.now()
        duration = end - self.start_time
        
        return duration.total_seconds()/3600
    
    
    def calculate_cost(self):
        hours = self.calculate_duration_hours()
        
        if self.price_per_hour_snapshot:
            price = self.price_per_hour_snapshot
        else :
            try:
                spot = ParkingSpot.query.get(self.spot_id)
                if spot and spot.lot:
                    price = spot.lot.price_per_hour
                else:
                    price = 0
            except:
                price = 0
        
        return round(hours * price)
    
    
    def get_lot_name(self):
        if self.lot_name_snapshot:
            return self.lot_name_snapshot
        try:
            return self.spot.lot.name
        except:
            return "Unknown Lot"
        
        
        
    def get_spot_number(self):
        if self.spot_number_snapshot:
            return self.spot_number_snapshot
        try:
            return self.spot.spot_number
        except:
            return "N/A"
        
    def save_snapshot(self):
        try:
            if self.spot and self.spot.lot:
                self.lot_name_snapshot = self.spot.lot.name
                self.spot_number_snapshot = self.spot.spot_number
            
                
                
        except:
            return "Adding Snapshot went fatally wrong"
        
        
        def __repr__(self):
            return f'<Reservation {self.id}, by user {self.user_id}>'
        
    
    
    
    
    