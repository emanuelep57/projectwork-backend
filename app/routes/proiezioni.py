from flask import Blueprint, jsonify, request
from ..models import Proiezione, Sala, Film
from datetime import datetime

bp = Blueprint('proiezioni', __name__)


@bp.route('', methods=['GET'])
def get_proiezioni():
    film_id = request.args.get('film_id')
    now = datetime.now()

    if not film_id:
        return jsonify({'error': 'Film ID is required'}), 400

    try:
        proiezioni = Proiezione.query \
            .filter_by(id_film=film_id) \
            .filter(Proiezione.data_ora > now) \
            .order_by(Proiezione.data_ora) \
            .all()

        return jsonify({
            'proiezioni': [{
                'id': p.id,
                'data_ora': p.data_ora.isoformat(),
                'costo': p.costo,
                'sala': Sala.query.get(p.id_sala).nome
            } for p in proiezioni]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:film_id>', methods=['GET'])
def get_film_proiezioni(film_id):
    proiezioni = Proiezione.query.filter_by(id_film=film_id).all()
    return jsonify([{
        'id': p.id,
        'data_ora': p.data_ora.isoformat(),
        'costo': p.costo,
        'sala': Sala.query.get(p.id_sala).nome
    } for p in proiezioni])
