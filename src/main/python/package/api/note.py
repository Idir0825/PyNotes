import os
import json
from uuid import uuid4
from glob import glob
from pathlib import Path

NOTES_DIR = os.path.join(Path.home(), ".notes")


def get_notes():
    """
	Récupère toutes les notes sur le disque
    :return grades: La liste de toutes les notes stockées sur le disque
    """
    grades = []
    # glob permet de récupérer tous les fichiers qui se trouvent dans le chemin
    # le chemin correspond à une concaténation de NOTES_DIR et de tous les fichiers se finissant par .json (d'ou le *)
    fichiers = glob(os.path.join(NOTES_DIR, "*.json"))
    for fichier in fichiers:
        with open(fichier, "r") as f:
            note_data = json.load(f)  # Dictionnaire avec le contenu du fichier
            note_uuid = os.path.splitext(os.path.basename(fichier))[
                0]  # On récupère uniquement le nom du fichier, puis on enlève l'extension
            note_title = note_data.get("title")  # L'avantage de get c'est qu'on a "none" si la valeur n'existe pas
            note_content = note_data.get("content")
            note_color = note_data.get("color")
            if not note_data.get("order"):
                note_order = "0"
            else:
                note_order = note_data.get("order")

            note = Note(uuid=note_uuid, title=note_title, content=note_content, order=note_order, color=note_color)
            grades.append(note)
    grades.sort(key=lambda x: int(x.order))
    return grades


class Note:
    """
	Créé une instance d'une note
    """

    def __init__(self, title="", content="", order="", color="", uuid=None):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = str(uuid4())
        self.title = title
        self.content = content
        self.order = order
        self.color = color

    def __repr__(self):
        return f"{self.title} (UUID={self.uuid}, order={self.order}, color={self.color})"

    def __str__(self):
        return self.title

    def change_color(self, color):
        self.color = color

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = value
        else:
            raise TypeError("Valeur invalide, besoin d'une chaîne de caractères.")

    def delete(self):
        os.remove(self.path)
        if os.path.exists(self.path):
            return False
        return True

    @property
    def path(self):
        return os.path.join(NOTES_DIR, self.uuid + ".json")

    def save(self):
        if not os.path.exists(NOTES_DIR):
            os.makedirs(NOTES_DIR)

        data = {"title": self.title, "content": self.content, "order": self.order, "color": self.color}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)  # Fonction pour écrire data dans fichier f au format json


if __name__ == '__main__':
    notes = get_notes()
    print(notes)
