from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from flask import current_app, Blueprint
from ..services.ordini_service import OrdiniService
from dataclasses import asdict

from ..utils.wrapper_login_required import login_required_restx

# Blueprint e Namespace
bp = Blueprint("ordini", __name__)
ordini_ns = Namespace('ordini', description='Operazioni sugli ordini')

# Modelli di risposta
biglietto_model = ordini_ns.model('Biglietto', {
    'id_posto': fields.Integer(required=True, description='ID del posto'),
    'nome_ospite': fields.String(description='Nome dell\'ospite'),
    'cognome_ospite': fields.String(description='Cognome dell\'ospite')
})

richiesta_aggiungi_biglietti = ordini_ns.model('RichiestaAggiungiBiglietti', {
    'biglietti': fields.List(fields.Nested(biglietto_model), required=True, description='Lista dei biglietti da aggiungere')
})

richiesta_rimuovi_posto = ordini_ns.model('RichiestaRimuoviPosto', {
    'idPosto': fields.Integer(required=True, description='ID del posto da rimuovere')
})

risposta_ordine = ordini_ns.model('RispostaOrdine', {
    'orders': fields.List(fields.Raw, description='Lista degli ordini')
})

risposta_pdf = ordini_ns.model('RispostaPdf', {
    'message': fields.String(description='Messaggio di successo'),
    'pdf_url': fields.String(description='URL del PDF generato')
})

risposta_errore = ordini_ns.model('RispostaErrore', {
    'error': fields.String(description='Messaggio di errore')
})


@ordini_ns.route('')
class ListaOrdini(Resource):
    @ordini_ns.response(200, 'Successo', risposta_ordine)
    @ordini_ns.response(500, 'Errore interno del server', risposta_errore)
    @login_required_restx
    def get(self):
        """Recupera tutti gli ordini dell'utente"""
        try:
            ordini = OrdiniService.get_ordini_utente()
            # Converto i DTO in dizionari
            return {'orders': [asdict(ordine) for ordine in ordini]}, 200
        except Exception as e:
            current_app.logger.error(f"Errore recupero ordini: {str(e)}")
            ordini_ns.abort(500, 'Impossibile recuperare gli ordini')


@ordini_ns.route('/<int:ordine_id>')
@ordini_ns.param('ordine_id', 'ID dell\'ordine')
class Ordine(Resource):
    @ordini_ns.response(200, 'Successo')
    @ordini_ns.response(400, 'Dati in input non validi', risposta_errore)
    @ordini_ns.response(500, 'Errore interno del server', risposta_errore)
    @login_required_restx
    def delete(self, ordine_id):
        """Elimina un ordine specifico"""
        try:
            OrdiniService.elimina_ordine(ordine_id, current_user.id)
            return {'message': 'Ordine eliminato con successo'}, 200
        except ValueError as e:
            ordini_ns.abort(400, str(e))
        except Exception as e:
            current_app.logger.error(f"Errore durante l'eliminazione dell'ordine: {str(e)}")
            ordini_ns.abort(500, 'Impossibile eliminare l\'ordine')


@ordini_ns.route('/<int:ordine_id>/aggiungi-posto')
@ordini_ns.param('ordine_id', 'ID dell\'ordine')
class AggiungiBiglietti(Resource):
    @ordini_ns.expect(richiesta_aggiungi_biglietti)
    @ordini_ns.response(200, 'Successo', risposta_pdf)
    @ordini_ns.response(400, 'Dati in input non validi', risposta_errore)
    @ordini_ns.response(500, 'Errore interno del server', risposta_errore)
    @login_required_restx
    def post(self, ordine_id):
        """Aggiunge biglietti a un ordine esistente"""
        try:
            dati = ordini_ns.payload
            if 'biglietti' not in dati:
                ordini_ns.abort(400, 'Dati biglietti mancanti')

            pdf_url = OrdiniService.aggiungi_biglietti(ordine_id, current_user.id, dati['biglietti'])
            return {
                'message': 'Biglietti aggiunti con successo',
                'pdf_url': pdf_url
            }, 200
        except ValueError as e:
            ordini_ns.abort(400, str(e))
        except Exception as e:
            current_app.logger.error(f"Errore aggiunta biglietti: {str(e)}")
            ordini_ns.abort(500, 'Impossibile aggiungere i biglietti all\'ordine')


@ordini_ns.route('/<int:ordine_id>/rimuovi-posto')
@ordini_ns.param('ordine_id', 'ID dell\'ordine')
class RimuoviPosto(Resource):
    @ordini_ns.expect(richiesta_rimuovi_posto)
    @ordini_ns.response(200, 'Successo', risposta_pdf)
    @ordini_ns.response(400, 'Dati in input non validi', risposta_errore)
    @ordini_ns.response(500, 'Errore interno del server', risposta_errore)
    @login_required_restx
    def post(self, ordine_id):
        """Rimuove un posto da un ordine esistente"""
        try:
            dati = ordini_ns.payload
            if 'idPosto' not in dati:
                ordini_ns.abort(400, 'ID posto mancante')

            pdf_url = OrdiniService.rimuovi_posto(ordine_id, current_user.id, dati['idPosto'])
            return {
                'message': 'Posto rimosso con successo',
                'pdf_url': pdf_url
            }, 200
        except ValueError as e:
            ordini_ns.abort(400, str(e))
        except Exception as e:
            current_app.logger.error(f"Errore durante la rimozione del posto: {str(e)}")
            ordini_ns.abort(500, 'Impossibile rimuovere il posto dall\'ordine')
