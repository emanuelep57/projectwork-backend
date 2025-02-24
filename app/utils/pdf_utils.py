import io
import qrcode
import requests
from flask import current_app
from flask_login import current_user
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as ReportlabImage, PageBreak
from reportlab.lib.enums import TA_CENTER

URL_LOGO = "https://res.cloudinary.com/dj5udxse6/image/upload/v1738162706/logo.webp"


def crea_stili_pdf():

    # documentazione sul paragraphstyle e sul samplestylesheet:
    # https://docs.reportlab.com/reportlab/userguide/ch6_paragraphs/
    stili = getSampleStyleSheet()

    if 'TitoloCustom' not in stili:
        stili.add(ParagraphStyle(
            'TitoloCustom',
            parent=stili['Heading1'],
            fontSize=16,
            textColor=black,
            alignment=TA_CENTER
        ))

    if 'SottotitoloCustom' not in stili:
        stili.add(ParagraphStyle(
            'SottotitoloCustom',
            parent=stili['Normal'],
            fontSize=12,
            textColor=black,
            alignment=TA_CENTER
        ))

    return stili


def genera_qr_code(dati):
    # il codice per generare il qr l'ho trovato presso la documentazione ufficiale
    # https://pypi.org/project/qrcode/
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    qr.add_data(dati)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # lo salvo in memoria
    buffer_img = io.BytesIO()
    img.save(buffer_img, format='PNG')
    buffer_img.seek(0)
    return buffer_img


# scarico la copertina e salvo anche quella in memoria
def scarica_immagine(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.RequestException as e:
        current_app.logger.error(f"Errore nel download dell'immagine: {e}")
        return None


def genera_biglietto_pdf(info_biglietti, id_ordine):

    if not info_biglietti:
        raise ValueError("Impossibile generare il PDF: nessun biglietto disponibile.")

    buffer_pdf = io.BytesIO()
    documento = SimpleDocTemplate(buffer_pdf, pagesize=letter)
    stili = crea_stili_pdf()
    contenuto = []

    for biglietto, film, proiezione, sala, posto in info_biglietti:
        contenuto_pagina = []

    # Scarico il logo e lo aggiungo
        logo_bytes = scarica_immagine(URL_LOGO)
        if logo_bytes:
            try:
                logo = ReportlabImage(logo_bytes, width=1.5 * inch, height=1.5 * inch)
                logo.hAlign = 'RIGHT'
                contenuto_pagina.append(logo)
            except Exception as e:
                current_app.logger.error(f"Errore nel caricamento del logo: {e}")

        # Stessa cosa con la copertina del film del film
        film_poster = scarica_immagine(film.url_copertina)
        if film_poster:
            try:
                poster = ReportlabImage(film_poster, width=3 * inch, height=4 * inch)
                poster.hAlign = 'CENTER'
                contenuto_pagina.append(poster)
            except Exception as e:
                current_app.logger.error(f"Errore nel caricamento della locandina: {e}")

        # Generazione del codice QR
        dati_qr = f"ID Biglietto: {biglietto.id}, Film: {film.titolo}, Data: {proiezione.data_ora}"
        qr_img = genera_qr_code(dati_qr)
        immagine_qr = ReportlabImage(qr_img, width=1.5 * inch, height=1.5 * inch)
        immagine_qr.hAlign = 'CENTER'

        # Siccome il primo biglietto non è mai dell'ospite, sarà sempe dell'utente
        # Per quelli che seguono invece se ci sono ospiti, prenderà prima loro.
        nome_ospite = f"{biglietto.nome_ospite or current_user.nome} {biglietto.cognome_ospite 
                                                                      or current_user.cognome}"

        # Aggiunta dei dettagli del biglietto
        contenuto_pagina.extend([
            Paragraph(f"Ordine ID: {id_ordine} - CINEMA PEGASUS", stili['TitoloCustom']),
            Paragraph(f"Film: {film.titolo}", stili['SottotitoloCustom']),
            Paragraph(f"Data: {proiezione.data_ora.strftime('%d/%m/%Y')}", stili['SottotitoloCustom']),
            Paragraph(f"Ora: {proiezione.data_ora.strftime('%H:%M')}", stili['SottotitoloCustom']),
            Paragraph(f"Sala: {sala.nome}", stili['SottotitoloCustom']),
            immagine_qr,
            Paragraph(f"Nome: {nome_ospite}", stili['SottotitoloCustom']),
            Paragraph(f"Posto: {posto.fila}{posto.numero}", stili['SottotitoloCustom']),
        ])

        # Aggiunta alla contenuto del documento
        contenuto.extend(contenuto_pagina)
        contenuto.append(PageBreak())

    # Generazione del PDF
    try:
        documento.build(contenuto)
    except Exception as e:
        current_app.logger.error(f"Errore nella generazione del PDF: {e}")
        raise ValueError("Errore durante la creazione del PDF.")

    #seek riporta il cursore del buffer all'inizio.
    buffer_pdf.seek(0)
    return buffer_pdf
