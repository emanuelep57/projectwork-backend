from datetime import datetime
from ..models import Biglietto, Film, Proiezione, Sala, Posto, db
from ..utils.cloudinary_utils import upload_pdf_to_cloudinary
from ..utils.pdf_utils import genera_biglietto_pdf


class BigliettiService:
    @staticmethod
    def acquista_biglietto(user_id, id_proiezione, biglietti_data, ordine_id):
        biglietti_acquistati = []
        id_biglietti = []

        for biglietto_data in biglietti_data:
            biglietto = Biglietto(
                id_proiezione=id_proiezione,
                id_utente=user_id,
                id_posto=biglietto_data['id_posto'],
                id_ordine=ordine_id,
                nome_ospite=biglietto_data.get('nome_ospite'),
                cognome_ospite=biglietto_data.get('cognome_ospite')
            )
            db.session.add(biglietto)
            db.session.flush()
            id_biglietti.append(biglietto.id)
            biglietti_acquistati.append(biglietto)

        tickets_info = (
            db.session.query(Biglietto, Film, Proiezione, Sala, Posto)
            .join(Proiezione, Biglietto.id_proiezione == Proiezione.id)
            .join(Film, Proiezione.id_film == Film.id)
            .join(Sala, Proiezione.id_sala == Sala.id)
            .join(Posto, Biglietto.id_posto == Posto.id)
            .filter(Biglietto.id.in_(id_biglietti))
            .all()
        )

        pdf_buffer = genera_biglietto_pdf(tickets_info, ordine_id)
        pdf_url = upload_pdf_to_cloudinary(pdf_buffer, f"ticket{ordine_id}{datetime.now()}")

        return id_biglietti, pdf_url
