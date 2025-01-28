from flask import Blueprint, jsonify, current_app, request
from flask_login import login_required, current_user
from sqlalchemy import and_

from ..models import Film, Biglietto, db, Ordine

bp = Blueprint('film', __name__)


@bp.route('/', methods=['GET'])
def get_films():
    films = Film.query.all()
    return jsonify([{
        'id': film.id,
        'titolo': film.titolo,
        'regista': film.regista,
        'url_copertina': film.url_copertina,
        'durata': film.durata,
        'descrizione': film.descrizione,
        'generi': film.generi
    } for film in films])


@bp.route('/<int:film_id>', methods=['GET'])
def get_film(film_id):
    film = Film.query.get(film_id)
    if not film:
        return jsonify({'error': 'Film not found'}), 404
    return jsonify({
        'id': film.id,
        'titolo': film.titolo,
        'regista': film.regista,
        'url_copertina': film.url_copertina,
        'durata': film.durata,
        'descrizione': film.descrizione,
        'generi': film.generi
    })

# Add to ordini.py


@bp.route('/change-projection-and-seats', methods=['POST'])
@login_required
def change_projection_and_seats():
    """Change both projection and seats for an entire order."""
    data = request.json
    try:
        # Validate order ownership
        order = Ordine.query.filter(
            and_(
                Ordine.id == data['order_id'],
                Ordine.id_utente == current_user.id
            )
        ).first()

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Validate new projection
        new_projection = Proiezione.query.get(data['new_projection_id'])
        if not new_projection:
            return jsonify({'error': 'Invalid projection'}), 400

        if new_projection.data_ora < datetime.now():
            return jsonify({'error': 'Cannot change to past projection'}), 400

        # Validate new seats
        new_seats = data['new_seats']
        current_tickets = Biglietto.query.filter_by(id_ordine=order.id).all()

        if len(new_seats) != len(current_tickets):
            return jsonify({'error': 'Invalid number of seats'}), 400

        # Check if seats are available in new projection
        occupied_seats = Biglietto.query.filter(
            and_(
                Biglietto.id_proiezione == new_projection.id,
                Biglietto.id_ordine != order.id
            )
        ).with_entities(Biglietto.id_posto).all()

        occupied_seat_ids = [seat[0] for seat in occupied_seats]

        for seat_id in new_seats:
            if seat_id in occupied_seat_ids:
                return jsonify({'error': 'One or more selected seats are already occupied'}), 400

        # Update order's projection
        order.id_proiezione = new_projection.id

        # Update tickets with new projection and seats
        for ticket, new_seat_id in zip(current_tickets, new_seats):
            ticket.id_proiezione = new_projection.id
            ticket.id_posto = new_seat_id

        db.session.commit()
        return jsonify({'message': 'Projection and seats updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Projection and seat change error: {str(e)}")
        return jsonify({'error': 'Failed to change projection and seats'}), 500