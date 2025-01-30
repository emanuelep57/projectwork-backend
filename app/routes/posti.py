from flask import Blueprint, jsonify
from ..services.posto_service import PostoService

bp = Blueprint('posti', __name__)


@bp.route('/<int:id_proiezione>', methods=['GET'])
def get_seats(id_proiezione):
    try:
        posti = PostoService.get_posti_proiezione(id_proiezione)
        return jsonify([posto.to_dict() for posto in posti])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/occupati/<int:projection_id>', methods=['GET'])
def get_occupied_seats(projection_id):
    try:
        posti_occupati = PostoService.get_posti_occupati(projection_id)
        return jsonify([posto.to_dict() for posto in posti_occupati])
    except Exception as e:
        return jsonify({'error': str(e)}), 500