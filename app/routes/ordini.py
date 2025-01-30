# routes/ordini.py
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from ..services.ordini_service import OrdiniService
from ..services.biglietti_service import BigliettiService

bp = Blueprint('ordini', __name__)


@bp.route('', methods=['GET'])
@login_required
def ottieni_ordini_utente():
    try:
        ordini = OrdiniService.get_ordini_utente()
        return jsonify({'orders': [ordine.__dict__ for ordine in ordini]}), 200
    except Exception as e:
        current_app.logger.error(f"Errore recupero ordini: {str(e)}")
        return jsonify({'error': 'Impossibile recuperare gli ordini'}), 500


@bp.route('/tickets/<int:id_biglietto>', methods=['DELETE'])
@login_required
def elimina_biglietto(id_biglietto):
    """Route per eliminare un biglietto."""
    try:
        BigliettiService.delete_ticket(id_biglietto, current_user.id)
        return jsonify({'message': 'Biglietto eliminato con successo'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Errore eliminazione biglietto: {str(e)}")
        return jsonify({'error': 'Impossibile eliminare il biglietto'}), 500


@bp.route('/change-projection-and-seats', methods=['POST'])
@login_required
def cambia_proiezione_e_posti():
    """Route per cambiare proiezione e posti di un ordine."""
    dati = request.json
    try:
        # Validazione dei dati richiesti
        required_fields = ['order_id', 'new_projection_id', 'new_seats']
        if not all(k in dati for k in required_fields):
            missing_fields = [field for field in required_fields if field not in dati]
            return jsonify({
                'error': f'Campi richiesti mancanti: {", ".join(missing_fields)}'
            }), 400

        # Validazione della struttura dei nuovi posti
        if not isinstance(dati['new_seats'], list):
            return jsonify({
                'error': 'Il campo new_seats deve essere una lista di posti'
            }), 400

        for seat in dati['new_seats']:
            if not isinstance(seat, dict) or 'id_posto' not in seat:
                return jsonify({
                    'error': 'Ogni posto deve contenere almeno id_posto'
                }), 400

        successo, messaggio = OrdiniService.cambia_proiezione_e_posti(
            dati['order_id'],
            current_user.id,
            dati['new_projection_id'],
            dati['new_seats']
        )

        return jsonify({'message': messaggio}), 200 if successo else 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Errore cambio proiezione e posti: {str(e)}")
        return jsonify({'error': 'Impossibile cambiare proiezione e posti'}), 500


@bp.route('/change-seats', methods=['POST'])
@login_required
def cambia_posti():
    """Route per cambiare i posti di un ordine."""
    dati = request.json
    try:
        # Validazione dei dati richiesti
        required_fields = ['order_id', 'new_seats']
        if not all(k in dati for k in required_fields):
            missing_fields = [field for field in required_fields if field not in dati]
            return jsonify({
                'error': f'Campi richiesti mancanti: {", ".join(missing_fields)}'
            }), 400

        # Validazione della struttura dei nuovi posti
        if not isinstance(dati['new_seats'], list):
            return jsonify({
                'error': 'Il campo new_seats deve essere una lista di posti'
            }), 400

        for seat in dati['new_seats']:
            if not isinstance(seat, dict) or 'id_posto' not in seat:
                return jsonify({
                    'error': 'Ogni posto deve contenere almeno id_posto'
                }), 400

        successo, messaggio = OrdiniService.cambia_posti(
            dati['order_id'],
            current_user.id,
            dati['new_seats']
        )

        return jsonify({'message': messaggio}), 200 if successo else 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Errore cambio posti: {str(e)}")
        return jsonify({'error': 'Impossibile cambiare i posti'}), 500
