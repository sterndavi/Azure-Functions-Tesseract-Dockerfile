import logging
import azure.functions as func
import pytesseract as pt
import requests
import tempfile
import pdf2image as p2i

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request')

    url_pdf = req.params.get('pdf_url')

    temp = tempfile.gettempdir()

    file = requests.get(url_pdf).content

    with open(f'{temp}/pdf_file.pdf', 'wb') as foto:
        foto.write(file)
        foto.close()

    p2i.convert_from_path(
        f'{temp}/pdf_file.pdf',
        500,
        output_folder = f"{temp}",
        output_file = "pdfphoto"
        )

    image_t_string = pt.image_to_string(
        f"{temp}/pdfphoto0001-1.ppm", lang= "por", 
        )

    return func.HttpResponse(
             str(image_t_string),
             status_code=200
    )