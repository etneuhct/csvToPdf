import csv
import base64
import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import *
from jinja2 import Template
import pdfkit
import re
import os

load_dotenv()


def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode()


def get_observations():
    with open("data/csv.csv", "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=',')
        i = 0
        data = []
        csv_reader = [item for item in csv_reader]
        for row in csv_reader:
            if i > 0:
                data.append({csv_reader[0][j]: row[j] for j in range(len(row))})
            i += 1
    return data


def generate_html(data, images):
    data = {**data, **images}
    with open("templates/pdf_template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())
    result = template.render(data)
    return result


def convert_html_to_pdf(html):
    pdfkit.from_string(html, "temp/out.pdf", {
        '--header-html': 'templates/header_pdf_template.html',
        '--footer-html': 'templates/footer_pdf_template.html',
        'footer-right': '[page] sur [topage]',
        'footer-left': '[date]',
        'footer-font-name': 'Calibri'
    })


def send_pdf(dest_mail, message_content):
    api_key = os.getenv("SENDGRID_API_KEY")
    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(os.getenv("SENDGRID_ADMIN_MAIL"))
    to_email = To(dest_mail)
    subject = "Rapport"
    content = Content("text/plain", message_content)
    mail = Mail(from_email, to_email, subject, content)
    file_path = 'temp/out.pdf'
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/pdf')
    attachment.file_name = FileName('rapport.pdf')
    attachment.disposition = Disposition('attachment')
    attachment.content_id = ContentId('id')
    mail.attachment = attachment
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)


def format_observation(raw_observation, variables):
    """
    On formate les données. Dans l'exemple, le saute de ligne sont remplacés par des balises
    """
    result = []
    regex = re.compile("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})")
    for variable in variables:
        if variable["code"] in raw_observation.keys():
            answer = raw_observation[variable['code']]
            search = re.search(regex, answer)
            if search:
                url = search.group()
                # answer = answer.replace(url, f'<a href="{url}" target="_blank">cliquez ici</a>')
            answer = answer.replace(".\n", ".<br>")
            question = variable["label"]

            result.append({"question": question, "answer": answer})
    raw_observation["variables"] = result
    return raw_observation


if __name__ == "__main__":

    # Assignation variable - label
    answer_variables = [
        {"code": "v1", "label": "Avez-vous des symptômes compatibles avec la COVID-19?"},
        {"code": "v2", "label": "Quelle est la situation de votre région?"},
        {"code": "v3", "label": "Êtes-vous plus à risque (plus vulnérable) que les autres face à la COVID-19?"},
        {"code": "v4", "label": "Vos habitudes de vie:"},
        {"code": "v5", "label": "Ceci est une question"},
        {"code": "v6", "label": "Ceci est une question"},
        {"code": "v7", "label": "Ceci est une question"},

    ]
    observations = get_observations()
    converted_images = {
        ".".join(item.split('.')[:-1]): image_to_base64(os.path.join("images", item)) for item in os.listdir("images")
    }

    with open("templates/message_template.txt", "r", encoding="utf-8") as text:
        text = Template(text.read())
    for observation in observations:
        observation = format_observation(observation, answer_variables)
        html_file = generate_html(observation, converted_images)
        convert_html_to_pdf(html_file)
        if os.path.exists("temp/out.pdf"):
            message = text.render(observation)
            send_pdf(observation["mail"], message)
            os.remove("temp/out.pdf")
