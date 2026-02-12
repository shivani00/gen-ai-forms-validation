import json
from config import MASTER_JSON_PATH


def load_full_json():
    with open(MASTER_JSON_PATH, "r") as f:
        return json.load(f)


def extract_form_json(full_json, form_id):

    for form in full_json["forms"]:
        if form["formId"] == form_id:
            return form["data"]

    return None