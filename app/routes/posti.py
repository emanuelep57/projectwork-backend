from flask import Blueprint
from flask_restx import Namespace, Resource, fields
from ..services.posto_service import PostoService

bp = Blueprint('posti', __name__)
posti_ns = Namespace('posti', description='Operazioni sui posti delle proiezioni')

# Definizione dei modelli per la documentazione openAPI
posto_model = posti_ns.model('Posto', {
    'id': fields.Integer(description='ID del posto'),
    'fila': fields.String(description='Fila del posto'),
    'numero': fields.Integer(description='Numero del posto')
})

posto_occupato_model = posti_ns.model('PostoOccupato', {
    'fila': fields.String(description='Fila del posto occupato'),
    'numero': fields.Integer(description='Numero del posto occupato')
})


@posti_ns.route('/<int:id_proiezione>')
@posti_ns.param('id_proiezione', 'ID della proiezione')
class PostiList(Resource):
    @posti_ns.doc('lista_posti')
    @posti_ns.response(200, 'Successo', [posto_model])
    @posti_ns.response(500, 'Errore interno del server')
    def get(self, id_proiezione):
        """Recupera tutti i posti per una specifica proiezione"""
        try:
            posti = PostoService.get_posti_proiezione(id_proiezione)
            return [posto.to_dict() for posto in posti]
        except Exception as e:
            posti_ns.abort(500, message=str(e))


@posti_ns.route('/occupati/<int:id_proiezione>')
@posti_ns.param('id_proiezione', 'ID della proiezione')
class PostiOccupati(Resource):
    @posti_ns.doc('lista_posti_occupati')
    @posti_ns.response(200, 'Successo', [posto_occupato_model])
    @posti_ns.response(500, 'Errore interno del server')
    def get(self, id_proiezione):
        """Recupera tutti i posti occupati per una specifica proiezione"""
        try:
            posti_occupati = PostoService.get_posti_occupati(id_proiezione)
            return [posto.to_dict() for posto in posti_occupati]
        except Exception as e:
            posti_ns.abort(500, message=str(e))
