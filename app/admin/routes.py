from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from app.extensions import db
from app.models import ParkingLot, ParkingSpot, Reservation, Payment, User
from .forms import ParkingLotForm, UpdateSpotsForm

from . import admin_bp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        lots = ParkingLot.query.all()
        total_lots = len(lots)
        total_spots = sum(lot.total_spots for lot in lots)
        active_bookings = Reservation.query.filter_by(is_active=True).count()
        
        # Calculate total earnings (paid)
        paid_payments = Payment.query.filter_by(is_paid=True).all()
        total_earnings = sum(p.amount for p in paid_payments)
        
        # Calculate total due (unpaid completed + active reservations)
        unpaid_payments = Payment.query.filter_by(is_paid=False).all()
        total_due_completed = sum(p.amount for p in unpaid_payments)
        
        # Active reservations ongoing cost
        active_reservations = Reservation.query.filter_by(is_active=True).all()
        total_due_active = 0
        for res in active_reservations:
            try:
                total_due_active += res.calculate_cost()
            except:
                pass
        
        total_due = total_due_completed + total_due_active
        
        return render_template('admin_dashboard.html', 
                             lots=lots,
                             total_lots=total_lots,
                             total_spots=total_spots,
                             active_bookings=active_bookings,
                             total_earnings=total_earnings,
                             total_due=total_due)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('admin_dashboard.html', 
                             lots=[], 
                             total_lots=0, 
                             total_spots=0, 
                             active_bookings=0,
                             total_earnings=0,
                             total_due=0)

@admin_bp.route('/add_lot', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lot():
    form = ParkingLotForm()
    if form.validate_on_submit():
        try:
            lot = ParkingLot(
                name=form.name.data,
                total_spots=form.total_spots.data,
                price_per_hour=form.price_per_hour.data
            )
            db.session.add(lot)
            db.session.flush()  # Get the lot ID
            
            # Create parking spots
            for i in range(1, form.total_spots.data + 1):
                spot = ParkingSpot(spot_number=i, lot_id=lot.id)
                db.session.add(spot)
            
            db.session.commit()
            flash(f'Parking lot "{lot.name}" added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('add_lot.html', form=form)

@admin_bp.route('/delete_lot/<int:lot_id>')
@login_required
@admin_required
def delete_lot(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        
        # Check if any spot is currently booked
        booked_count = sum(1 for spot in lot.spots if spot.is_booked)
        if booked_count > 0:
            flash(f'Cannot delete lot. {booked_count} spot(s) are currently booked.', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        # Before deletion, ensure all reservations have snapshots
        for spot in lot.spots:
            for reservation in spot.reservations:
                if not reservation.lot_name_snapshot:
                    reservation.save_snapshot()
        
        db.session.commit()
        
        # Now safe to delete
        db.session.delete(lot)
        db.session.commit()
        flash(f'Parking lot "{lot.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_spots/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_spots(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        form = UpdateSpotsForm()
        
        if form.validate_on_submit():
            new_total = form.total_spots.data
            current_booked = lot.get_booked_spots_count()
            
            if new_total < current_booked:
                flash(f'Cannot reduce spots below {current_booked} (currently booked).', 'danger')
                return redirect(url_for('admin.update_spots', lot_id=lot_id))
            
            if new_total > lot.total_spots:
                # Add new spots
                for i in range(lot.total_spots + 1, new_total + 1):
                    spot = ParkingSpot(spot_number=i, lot_id=lot.id)
                    db.session.add(spot)
            elif new_total < lot.total_spots:
                # Remove spots (from the end, unbooked only)
                spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, is_booked=False)\
                    .order_by(ParkingSpot.spot_number.desc())\
                    .limit(lot.total_spots - new_total).all()
                for spot in spots_to_remove:
                    db.session.delete(spot)
            
            lot.total_spots = new_total
            db.session.commit()
            flash(f'Updated spots for "{lot.name}" to {new_total}.', 'success')
            return redirect(url_for('admin.dashboard'))
        
        form.total_spots.data = lot.total_spots
        return render_template('update_spots.html', form=form, lot=lot)
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/bookings')
@login_required
@admin_required
def view_bookings():
    try:
        bookings = Reservation.query.order_by(Reservation.start_time.desc()).all()
        
        # Add cost to each booking as an attribute for template
        for booking in bookings:
            try:
                booking.cost = booking.calculate_cost()
                booking.duration = booking.calculate_duration_hours()
            except:
                booking.cost = 0
                booking.duration = 0
        
        return render_template('view_bookings.html', bookings=bookings)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('view_bookings.html', bookings=[])

@admin_bp.route('/active_bookings')
@login_required
@admin_required
def active_bookings():
    try:
        # Get all active reservations
        active_reservations = Reservation.query.filter_by(is_active=True)\
            .order_by(Reservation.start_time.desc()).all()
        
        # Calculate costs and add as attributes
        total_cost = 0
        for res in active_reservations:
            try:
                res.cost = res.calculate_cost()
                res.duration = res.calculate_duration_hours()
                total_cost += res.cost
            except Exception as e:
                res.cost = 0
                res.duration = 0
        
        return render_template('active_bookings.html', 
                             reservations=active_reservations,
                             total_cost=total_cost)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('active_bookings.html', reservations=[], total_cost=0)

@admin_bp.route('/due_payments')
@login_required
@admin_required
def due_payments():
    try:
        # Get unpaid completed reservations
        unpaid_payments = Payment.query.filter_by(is_paid=False).all()
        
        # Get active reservations (ongoing cost)
        active_reservations = Reservation.query.filter_by(is_active=True).all()
        
        # Add costs and durations as attributes
        for res in active_reservations:
            try:
                res.cost = res.calculate_cost()
                res.duration = res.calculate_duration_hours()
            except:
                res.cost = 0
                res.duration = 0
        
        for payment in unpaid_payments:
            try:
                payment.reservation.duration = payment.reservation.calculate_duration_hours()
            except:
                payment.reservation.duration = 0
        
        # Calculate totals
        total_due_completed = sum(p.amount for p in unpaid_payments)
        total_due_active = sum(r.cost for r in active_reservations)
        total_due = total_due_completed + total_due_active
        
        return render_template('due_payments.html',
                             unpaid_payments=unpaid_payments,
                             active_reservations=active_reservations,
                             total_due_completed=total_due_completed,
                             total_due_active=total_due_active,
                             total_due=total_due)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('due_payments.html',
                             unpaid_payments=[],
                             active_reservations=[],
                             total_due_completed=0,
                             total_due_active=0,
                             total_due=0)

@admin_bp.route('/earnings')
@login_required
@admin_required
def earnings_report():
    try:
        # Get all paid payments
        paid_payments = Payment.query.filter_by(is_paid=True)\
            .order_by(Payment.payment_date.desc()).all()
        
        # Add duration to each payment's reservation
        for payment in paid_payments:
            try:
                payment.reservation.duration = payment.reservation.calculate_duration_hours()
            except:
                payment.reservation.duration = 0
        
        total_earnings = sum(p.amount for p in paid_payments)
        
        # Get unpaid for reference
        unpaid_count = Payment.query.filter_by(is_paid=False).count()
        unpaid_payments = Payment.query.filter_by(is_paid=False).all()
        total_due = sum(p.amount for p in unpaid_payments)
        
        # Add active reservations to due
        active_reservations = Reservation.query.filter_by(is_active=True).all()
        for res in active_reservations:
            try:
                total_due += res.calculate_cost()
            except:
                pass
        
        total_revenue = total_earnings + total_due
        
        return render_template('earnings_report.html',
                             paid_payments=paid_payments,
                             total_earnings=total_earnings,
                             total_due=total_due,
                             total_revenue=total_revenue,
                             unpaid_count=unpaid_count)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('earnings_report.html',
                             paid_payments=[],
                             total_earnings=0,
                             total_due=0,
                             total_revenue=0,
                             unpaid_count=0)

@admin_bp.route('/lot_grid/<int:lot_id>')
@login_required
@admin_required
def lot_grid(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        return render_template('lot_grid.html', lot=lot)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))