from flask import request
from flask_restx import Namespace, Resource, fields
from ..services.proiezione_service import ProiezioneService

proiezioni_ns = Namespace('proiezioni', description='Operazioni sulle proiezioni')

# Definizione dei modelli per la documentazione openAPI
proiezione_model = proiezioni_ns.model('Proiezione', {
    'id': fields.Integer(description='ID della proiezione'),
    'data_ora': fields.String(description='Data e ora della proiezione'),
    'costo': fields.Float(description='Costo della proiezione'),
    'sala': fields.String(description='Nome della sala')
})


@proiezioni_ns.route('/')
class ProiezioneList(Resource):
    @proiezioni_ns.param('film_id', 'ID del film', type=int, required=True)
    @proiezioni_ns.response(200, 'Successo', [proiezione_model])
    @proiezioni_ns.response(400, 'Errore sui dati in ingresso')
    @proiezioni_ns.response(500, 'Errore interno del server')
    def get(self):
        """Recupera le proiezioni future di un film specifico"""
        film_id = request.args.get('film_id', type=int)
        if film_id is None:
            return {'errore': 'L\id del film non è presente'}, 400

        try:
            proiezioni = ProiezioneService.get_proiezioni(film_id)
            return [p.to_dict() for p in proiezioni]
        except Exception as e:
            return {'error': str(e)}, 500
