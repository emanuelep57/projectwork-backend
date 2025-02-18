from flask import request, current_app
from flask_login import current_user
from ..services.biglietti_service import BigliettiService
from ..services.ordini_service import OrdiniService
from ..models import db
from flask_restx import Namespace, Resource, fields

from ..utils.wrapper_login_required import login_required_restx

biglietti_ns = Namespace('biglietti', description='Operazioni relative ai biglietti')

# Definizione dei modelli per la documentazione
posto_in_biglietto_model = biglietti_ns.model('PostoInBiglietto', {
    'id_posto': fields.Integer(required=True, description='ID del posto'),
    'nome_ospite': fields.String(required=False, description='Nome dell\'ospite'),
    'cognome_ospite': fields.String(required=False, description='Cognome dell\'ospite')
})

acquisto_biglietto_input = biglietti_ns.model('AcquistoBigliettoInput', {
    'id_proiezione': fields.Integer(required=True, description='ID della proiezione'),
    'biglietti': fields.List(fields.Nested(posto_in_biglietto_model), required=True, description='Lista di biglietti da acquistare')
})

acquisto_biglietto_output = biglietti_ns.model('AcquistoBigliettoOutput', {
    'id_biglietti': fields.List(fields.Integer, description='Lista degli ID dei biglietti acquistati'),
    'pdf_urls': fields.List(fields.String, description='URL del PDF del biglietto')
})

error_model = biglietti_ns.model('Error', {
    'error': fields.String(description='Messaggio di errore')
})


@biglietti_ns.route('/acquisto')
class AcquistoBiglietto(Resource):
    @login_required_restx
    @biglietti_ns.doc(description='Acquista uno o più biglietti per una proiezione')
    @biglietti_ns.expect(acquisto_biglietto_input)
    @biglietti_ns.response(200, 'Successo', acquisto_biglietto_output)
    @biglietti_ns.response(400, 'Dati in input non validi', error_model)
    @biglietti_ns.response(500, 'Errore del server', error_model)
    def post(self):
        data = request.json

        if not data.get('biglietti'):
            return {'errore': 'I dati in input non sono validi'}, 400

        try:
            ordine = OrdiniService.crea_ordine(
                user_id=current_user.id,
                id_proiezione=data['id_proiezione']
            )

            id_biglietti, pdf_url = BigliettiService.acquista_biglietto(
                current_user.id,
                data['id_proiezione'],
                data['biglietti'],
                ordine.id
            )

            ordine.pdf_url = pdf_url
            db.session.commit()

            return {
                'id_biglietti': id_biglietti,
                'pdf_urls': [pdf_url]
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Errore durante l\'acqusito: {str(e)}")
            return {'errore': str(e)}, 500
