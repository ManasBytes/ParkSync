from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ParkingLot, ParkingSpot, Reservation, Payment
from app.user.forms import BookingForm
from datetime import datetime

from . import user_bp

def check_not_admin():
    if current_user.is_admin:
        flash('Admins cannot access user pages.', 'warning')
        abort(403)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    check_not_admin()
    
    try:
        # Get all parking lots
        lots = ParkingLot.query.all()
        
        # Get user's active reservation
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
        
        # Get previous reservations
        previous_reservations = Reservation.query.filter_by(
            user_id=current_user.id,
            is_active=False
        ).order_by(Reservation.end_time.desc()).all()
        
        return render_template('user_dashboard.html', 
                             lots=lots, 
                             active_reservation=active_reservation,
                             previous_reservations=previous_reservations)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return render_template('user_dashboard.html', lots=[], active_reservation=None, previous_reservations=[])
    
    
    
    
    
    
    

@user_bp.route('/book/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def book_lot(lot_id):
    check_not_admin()
    
    try:
        # Check if user already has an active booking
        active_reservation = Reservation.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if active_reservation:
            flash('You already have an active booking. Please check out first.', 'warning')
            return redirect(url_for('user.dashboard'))
        
        lot = ParkingLot.query.get_or_404(lot_id)
        form = BookingForm()
        
        if form.validate_on_submit():
            spot = ParkingSpot.query.get(form.spot_id.data)
            if not spot or spot.is_booked:
                flash('This spot is no longer available.', 'danger')
                return redirect(url_for('user.book_lot', lot_id=lot_id))
            
            # Create reservation with snapshot
            reservation = Reservation(
                user_id=current_user.id,
                spot_id=spot.id,
                vehicle_number=form.vehicle_number.data
            )
            reservation.save_snapshot()  # Save lot and spot details
            spot.is_booked = True
            
            db.session.add(reservation)
            db.session.commit()
            
            flash(f'Successfully booked Spot {spot.spot_number}!', 'success')
            return redirect(url_for('user.dashboard'))
        
        return render_template('booking.html', lot=lot, form=form)
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))








@user_bp.route('/checkout/<int:reservation_id>')
@login_required
def checkout(reservation_id):
    check_not_admin()
    
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        
        if reservation.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        if not reservation.is_active:
            flash('This reservation is already checked out.', 'warning')
            return redirect(url_for('user.dashboard'))
        
        # End reservation
        reservation.end_time = datetime.utcnow()
        reservation.is_active = False
        
        # Free up the spot
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.is_booked = False
        
        # Calculate payment
        amount = reservation.calculate_cost()
        payment = Payment(
            reservation_id=reservation.id,
            amount=amount,
            is_paid=False
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Redirect to payment options page
        return redirect(url_for('user.payment_options', payment_id=payment.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))







@user_bp.route('/payment_options/<int:payment_id>')
@login_required
def payment_options(payment_id):
    check_not_admin()
    
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Verify ownership
        if payment.reservation.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        return render_template('payment_options.html', payment=payment)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))







@user_bp.route('/pay_now/<int:payment_id>')
@login_required
def pay_now(payment_id):
    check_not_admin()
    
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Verify ownership
        if payment.reservation.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Mark as paid
        payment.is_paid = True
        payment.payment_date = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Payment of ${payment.amount:.2f} successful! Thank you.', 'success')
        return redirect(url_for('user.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))






@user_bp.route('/pay_later/<int:payment_id>')
@login_required
def pay_later(payment_id):
    check_not_admin()
    
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Verify ownership
        if payment.reservation.user_id != current_user.id:
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Payment remains unpaid (is_paid=False by default)
        flash(f'Payment of ${payment.amount:.2f} marked as due. You can pay later.', 'info')
        return redirect(url_for('user.dashboard'))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('user.dashboard'))