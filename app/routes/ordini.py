from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import and_

from ..models import Ordine, Proiezione, Film, Biglietto, db, Posto

bp = Blueprint('ordini', __name__)


def create_order(user_id, projection_id):
    """Create an order for movie tickets."""
    try:
        # Create order without total
        ordine = Ordine(
            id_utente=user_id,
            id_proiezione=projection_id
        )
        db.session.add(ordine)
        db.session.flush()  # Assign an ID to the order

        return ordine

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Order creation error: {str(e)}")
        raise


@bp.route('', methods=['GET'])
@login_required
def get_user_orders():
    try:
        orders = db.session.query(
            Ordine, Proiezione, Film
        ).join(Proiezione, Ordine.id_proiezione == Proiezione.id) \
            .join(Film, Proiezione.id_film == Film.id) \
            .filter(Ordine.id_utente == current_user.id) \
            .order_by(Ordine.data_acquisto.desc()) \
            .all()

        order_list = []
        for order, proiezione, film in orders:
            # Get tickets for this order
            tickets = Biglietto.query.filter_by(id_ordine=order.id).all()

            order_details = {
                'id': order.id,
                'data_acquisto': order.data_acquisto.isoformat(),
                'pdf_url': order.pdf_url,
                'proiezione': {
                    'id': proiezione.id,
                    'film_id': film.id,  # Aggiungiamo questo
                    'film_titolo': film.titolo,
                    'data_ora': proiezione.data_ora.isoformat(),
                    'costo': float(proiezione.costo)
                },
                'biglietti': [{
                    'id': ticket.id,
                    'posto': f"{ticket.posto.fila}{ticket.posto.numero}",
                    'nome_ospite': ticket.nome_ospite,
                    'cognome_ospite': ticket.cognome_ospite
                } for ticket in tickets]
            }

            order_list.append(order_details)

        return jsonify({
            'orders': order_list
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500


@bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    """Delete a ticket for a future projection."""
    try:
        # Find ticket belonging to current user
        ticket = Biglietto.query.filter(
            and_(
                Biglietto.id == ticket_id,
                Biglietto.id_utente == current_user.id
            )
        ).first()

        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Check projection time
        proiezione = Proiezione.query.get(ticket.id_proiezione)
        if proiezione.data_ora < datetime.now():
            return jsonify({'error': 'Cannot delete ticket for past projections'}), 400

        # Remove ticket
        db.session.delete(ticket)

        # Optional: Delete order if no tickets remain
        remaining_tickets = Biglietto.query.filter_by(id_ordine=ticket.id_ordine).count()
        if remaining_tickets <= 1:
            order = Ordine.query.get(ticket.id_ordine)
            db.session.delete(order)

        db.session.commit()
        return jsonify({'message': 'Ticket successfully deleted'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting ticket: {str(e)}")
        return jsonify({'error': 'Failed to delete ticket'}), 500


def validate_seats_availability(projection_id, seat_ids, exclude_order_id=None):
    """
    Validate that selected seats are available for the given projection.

    Args:
        projection_id: ID of the projection to check
        seat_ids: List of seat IDs to validate
        exclude_order_id: Optional order ID to exclude from occupied seats check

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        # Get all occupied seats for this projection
        occupied_seats_query = db.session.query(Biglietto.id_posto).filter(
            Biglietto.id_proiezione == projection_id
        )

        # Exclude seats from current order if updating
        if exclude_order_id:
            occupied_seats_query = occupied_seats_query.filter(
                Biglietto.id_ordine != exclude_order_id
            )

        occupied_seats = set(row[0] for row in occupied_seats_query.all())

        # Check if any selected seat is already occupied
        for seat_id in seat_ids:
            if seat_id in occupied_seats:
                seat = Posto.query.get(seat_id)
                return False, f"Seat {seat.fila}{seat.numero} is already taken"

        return True, ""

    except Exception as e:
        current_app.logger.error(f"Seat validation error: {str(e)}")
        return False, "Error validating seats"


@bp.route('/change-projection-and-seats', methods=['POST'])
@login_required
def change_projection_and_seats():
    """Change both projection and seats for an order."""
    data = request.json
    try:
        # Validate request data
        if not all(k in data for k in ['order_id', 'new_projection_id', 'new_seats']):
            return jsonify({'error': 'Missing required fields'}), 400

        order = Ordine.query.filter(
            and_(
                Ordine.id == data['order_id'],
                Ordine.id_utente == current_user.id
            )
        ).first()

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        new_projection = Proiezione.query.get(data['new_projection_id'])
        if not new_projection:
            return jsonify({'error': 'Invalid projection'}), 400

        # Validate projection is in the future
        if new_projection.data_ora < datetime.now():
            return jsonify({'error': 'Cannot change to past projection'}), 400

        # Validate number of seats matches current tickets
        current_tickets = Biglietto.query.filter_by(id_ordine=order.id).count()
        if len(data['new_seats']) != current_tickets:
            return jsonify({'error': 'Number of seats must match current tickets'}), 400

        # Validate seat availability
        is_valid, error_message = validate_seats_availability(
            new_projection.id,
            data['new_seats']
        )
        if not is_valid:
            return jsonify({'error': error_message}), 400

        # Update order's projection
        order.id_proiezione = new_projection.id

        # Update all tickets with new projection and seats
        tickets = Biglietto.query.filter_by(id_ordine=order.id).all()
        for ticket, new_seat_id in zip(tickets, data['new_seats']):
            ticket.id_proiezione = new_projection.id
            ticket.id_posto = new_seat_id

        db.session.commit()
        return jsonify({'message': 'Projection and seats updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Projection and seats change error: {str(e)}")
        return jsonify({'error': 'Failed to change projection and seats'}), 500


@bp.route('/change-seats', methods=['POST'])
@login_required
def change_seats():
    """Change seats for an existing order."""
    data = request.json
    try:
        if not all(k in data for k in ['order_id', 'new_seats']):
            return jsonify({'error': 'Missing required fields'}), 400

        order = Ordine.query.filter(
            and_(
                Ordine.id == data['order_id'],
                Ordine.id_utente == current_user.id
            )
        ).first()

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Validate number of seats matches current tickets
        current_tickets = Biglietto.query.filter_by(id_ordine=order.id).count()
        if len(data['new_seats']) != current_tickets:
            return jsonify({'error': 'Number of seats must match current tickets'}), 400

        # Validate seat availability
        is_valid, error_message = validate_seats_availability(
            order.id_proiezione,
            data['new_seats'],
            order.id
        )
        if not is_valid:
            return jsonify({'error': error_message}), 400

        # Update tickets with new seats
        tickets = Biglietto.query.filter_by(id_ordine=order.id).all()
        for ticket, new_seat_id in zip(tickets, data['new_seats']):
            ticket.id_posto = new_seat_id

        db.session.commit()
        return jsonify({'message': 'Seats updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Seats change error: {str(e)}")
        return jsonify({'error': 'Failed to change seats'}), 500