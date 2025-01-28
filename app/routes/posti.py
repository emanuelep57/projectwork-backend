from flask import Blueprint, jsonify
from ..models import Posto, Biglietto, Proiezione, Sala

bp = Blueprint('posti', __name__)


@bp.route('/<int:id_proiezione>', methods=['GET'])
def get_seats(id_proiezione):
    posti = Posto.query.join(Sala, Sala.id == Posto.id_sala) \
        .join(Proiezione, Proiezione.id_sala == Sala.id) \
        .filter(Proiezione.id == id_proiezione).all()

    # Itera correttamente sui singoli elementi della lista `posti`
    return jsonify([{
        'id': posto.id,       # Accedi al singolo oggetto `Posto`
        'fila': posto.fila,
        'numero': posto.numero,
    } for posto in posti])  # Usa `posto` invece di `posti`


@bp.route('/occupati/<int:projection_id>', methods=['GET'])
def get_occupied_seats(projection_id):
    # Query to get all occupied seats for a specific projection
    occupied_seats = Posto.query \
        .join(Biglietto, Biglietto.id_posto == Posto.id) \
        .filter(Biglietto.id_proiezione == projection_id) \
        .all()

    # Format the response
    seats = [{'fila': seat.fila, 'numero': seat.numero} for seat in occupied_seats]

    return jsonify(seats)
