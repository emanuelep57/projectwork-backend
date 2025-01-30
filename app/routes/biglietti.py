from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from ..services.biglietti_service import BigliettiService
from ..services.ordini_service import OrdiniService
from ..models import db

bp = Blueprint('biglietti', __name__)

@bp.route('/acquisto', methods=['POST'])
@login_required
def acquista_biglietto():
    data = request.json

    if not data.get('biglietti'):
        return jsonify({'error': 'No tickets provided'}), 400

    try:
        ordine = OrdiniService.create_order(
            user_id=current_user.id,
            projection_id=data['id_proiezione']
        )

        ticket_ids, pdf_url = BigliettiService.acquista_biglietto(
            current_user.id,
            data['id_proiezione'],
            data['biglietti'],
            ordine.id
        )

        ordine.pdf_url = pdf_url
        db.session.commit()

        return jsonify({
            'ticket_ids': ticket_ids,
            'pdf_urls': [pdf_url]
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Purchase error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['GET'])
@login_required
def get_user_tickets():
    try:
        upcoming_tickets, past_tickets = BigliettiService.get_user_tickets(current_user.id)
        return jsonify({
            'upcoming_tickets': [ticket.__dict__ for ticket in upcoming_tickets],
            'past_tickets': [ticket.__dict__ for ticket in past_tickets]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching tickets: {str(e)}")
        return jsonify({'error': 'Failed to retrieve tickets'}), 500


@bp.route('/pdfs', methods=['GET'])
@login_required
def get_ticket_pdfs():
    try:
        pdf_urls = BigliettiService.get_ticket_pdfs(current_user.id)
        return jsonify({'pdf_urls': pdf_urls}), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving ticket PDFs: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ticket PDFs'}), 500


@bp.route('/<int:ticket_id>/pdf-url', methods=['GET'])
@login_required
def get_ticket_pdf_url(ticket_id):
    try:
        pdf_url = BigliettiService.get_ticket_pdf_url(ticket_id, current_user.id)
        return jsonify({'pdf_url': pdf_url}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error retrieving ticket PDF: {str(e)}")
        return jsonify({'error': 'Failed to retrieve ticket PDF'}), 500


@bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    try:
        BigliettiService.delete_ticket(ticket_id, current_user.id)
        return jsonify({'message': 'Ticket successfully deleted'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting ticket: {str(e)}")
        return jsonify({'error': 'Failed to delete ticket'}), 500