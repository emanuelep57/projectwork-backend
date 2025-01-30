from flask import Blueprint, jsonify, request
from ..services.proiezione_service import ProiezioneService

bp = Blueprint('proiezioni', __name__)


@bp.route('/<int:film_id>', methods=['GET'])
def get_proiezioni_film(film_id):
    try:
        proiezioni = ProiezioneService.get_proiezioni(film_id)
        return jsonify([p.to_dict() for p in proiezioni])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
