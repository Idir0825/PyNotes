import os
from glob import glob

from PySide2 import QtWidgets, QtGui, QtCore

from package.api.note import Note, get_notes

COLORS = {
        "10": ("#D91B0B", (217, 27, 11)),
        "11": ("#F1948A", (241, 148, 138)),
        "12": ("#8E44AD", (142, 68, 173)),
        "13": ("#BB8FCE", (187, 143, 206)),
        "14": ("#0FCDAD", (15, 205, 173)),
        "15": ("#0D2699", (13, 38, 153)),
        "16": ("#0B0562", (11, 5, 98)),
        "17": ("#76D7C4", (118, 215, 196)),
        "18": ("#0C7611", (12, 118, 17)),
        "19": ("#073207", (7, 50, 7)),
        "20": ("#F1C40F", (241, 196, 15)),
        "21": ("#CF8A00", (207, 138, 0)),
        "22": ("#734D17", (115, 77, 23)),
        "23": ("#FFFFFF", (255, 255, 255)),
        "24": ("#CACFD2", (202, 207, 210)),
        "25": ("#000000", (0, 0, 0))
}


class NoteItem(QtWidgets.QListWidgetItem):

    def __init__(self, name, list_widget, note, color=""):
        super().__init__(name)
        self.list_widget = list_widget
        self.name = name
        self.color = color
        self.note = note
        self.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.setSizeHint(QtCore.QSize(0, 25))  # Permet de changer la taille de l'élément

        self.list_widget.addItem(self)

        if self.color:
            self.set_background_color()

    def set_background_color(self):
        color = (self.color[0], self.color[1], self.color[2])

        if color not in [(255, 255, 255), [255, 255, 255], (202, 207, 210), [202, 207, 210]]:
            front_color = "#FFFFFF"
        else:
            front_color = "#000000"

        self.setBackgroundColor(QtGui.QColor(*color))
        stylesheet = f""" QListView::item:selected {{background: rgb{color[0], color[1], color[2]}; 
        color: {front_color}; 
        border: 1px solid #FFFFFF; }}"""
        # Les :: signifient qu'on veut affecter uniquement les items, et pas tout le liste view, le : signifie qu'on veut affecter un événement
        # On utilise le CSS pour pouvoir mettre une couleur de sélection qui soit la même que la couleur qui montre si l'item est fini ou non
        self.list_widget.setStyleSheet(stylesheet)
        self.note.save()


class MainWindow(QtWidgets.QWidget):
    """
        MainWindow of the application
    """

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx  # Cette variable correspond au "contexte" à l'application en elle même
        self.setWindowTitle("PyNotes")
        self.setup_ui()
        self.populate_notes()

    # -- START UI --
    def setup_ui(self):
        """
            Execution of the UI building functions
        """
        self.create_widgets()
        self.create_layouts()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        """
            Creating all the widgets used in the MainWindow
        """
        self.btn_createNote = QtWidgets.QPushButton("Créer une note")
        self.lw_notes = QtWidgets.QListWidget()
        self.te_contenu = QtWidgets.QTextEdit()
        self.splitter = QtWidgets.QSplitter()

        self.confirmationBox = QtWidgets.QMessageBox(parent=self)
        self.confirmationBox.setText("Suppression !")
        self.confirmationBox.setInformativeText("Les notes sélectionnées seront supprimées, poursuivre ?")
        self.btn_yes = self.confirmationBox.addButton("Oui", QtWidgets.QMessageBox.ActionRole)
        self.btn_no = self.confirmationBox.addButton("Non", QtWidgets.QMessageBox.ActionRole)

        self.rc_menu = QtWidgets.QMenu()
        self.rc_menu_add = QtWidgets.QAction("Ajouter une note")
        self.rc_menu_delete = QtWidgets.QAction("Supprimer")
        self.rc_menu_rename = QtWidgets.QAction("Renommer")

        self.rc_menu_colors = QtWidgets.QMenu("Couleur")

        self.colors = glob(os.path.join(self.ctx.get_resource(), "*.svg"))  # Getting the icons' pathnames

        self.rc_menu_color_choices = {}
        for color in self.colors:
            number = os.path.basename(color)[0:2]
            self.rc_menu_color_choices[QtWidgets.QAction(icon=QtGui.QIcon(color))] = COLORS[number][1]
            # rc_menu_color_choices = {RED_MENU_ACTION: RED_COLOR_CODE), PINK_MENU_ACTION: PINK_COLOR_CODE,..}

        self.fatal_error_message = QtWidgets.QMessageBox()
        self.fatal_error_message.setWindowTitle("Oops !")
        self.fatal_error_message.setText("Veuillez redémarrer l'application")

    def modify_widgets(self):
        """
            Modifying the created widgets
        """
        css_file = self.ctx.get_resource("style.css")  # ça va bien dans 'resources/base/
        with open(css_file, "r") as f:
            self.setStyleSheet(f.read())

        self.lw_notes.installEventFilter(self)
        self.lw_notes.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)  # Permet de changer l'ordre des items

    def create_layouts(self):
        """
            Creating the layouts
        """
        self.main_layout = QtWidgets.QGridLayout(self)

    def add_widgets_to_layouts(self):
        """
            Adding the created widgets to the layouts
        """
        self.main_layout.addWidget(self.btn_createNote)
        self.main_layout.addWidget(self.splitter)
        self.splitter.addWidget(self.lw_notes)
        self.splitter.addWidget(self.te_contenu)
        self.splitter.setSizes([self.width() / 3, self.width() * (2 / 3)])

        self.rc_menu.addAction(self.rc_menu_add)
        self.rc_menu.addAction(self.rc_menu_delete)
        self.rc_menu.addAction(self.rc_menu_rename)
        self.rc_menu.addMenu(self.rc_menu_colors)

        for action in self.rc_menu_color_choices.keys():
            self.rc_menu_colors.addAction(action)

    def setup_connections(self):
        """
            Creating the connections
        """
        self.btn_createNote.clicked.connect(self.create_note)
        self.te_contenu.textChanged.connect(self.save_note)
        self.lw_notes.itemSelectionChanged.connect(self.populate_note_content)
        QtWidgets.QShortcut(QtGui.QKeySequence("BackSpace"), self.lw_notes,
                            self.delete_selected_note)  # On créé un shortcut, avec la touche Backspace, on lie la
        # fonction delete à la liste lw_notes

        self.rc_menu_add.triggered.connect(self.create_note)
        self.rc_menu_delete.triggered.connect(self.delete_selected_note)
        self.rc_menu_rename.triggered.connect(self.rename_note)

        for action, color in self.rc_menu_color_choices.items():
            action.triggered.connect(self.make_change_note_color(color))

    # -- END UI --

    def add_note_to_listwidget(self, note):
        """
            Adds the note to the listwidget so that it appears on the UI without having to restart the app
        :param note:
        """
        lw_item = NoteItem(name=note.title, color=note.color, list_widget=self.lw_notes, note=note)

    def make_change_note_color(self, color):
        """ Make the change_note_color function for each button of the contextual menu """
        def change_note_color():
            """ Function to change the color of an item in the list widget """
            selected_item = self.get_selected_lw_item()
            selected_item.note.change_color(color)
            selected_item.color = color
            self.color_changer(selected_item)

        return change_note_color

    def change_notes_order(self):
        """
            Updating the notes order
        """
        try:
            for i in range(0, self.lw_notes.count()):
                self.lw_notes.item(i).note.order = i
            self.populate_note_content()
        except Exception as e:
            self.fatal_error_message.setInformativeText(f"{e}")
            self.fatal_error_message.show()
            self.destroy()

    def color_changer(self, item: QtWidgets.QListWidgetItem):
        """
        Change the background color of the item in the list, and its foreground color depending on the background color
        :param item: A list widget item, the one that is currently selected
        """

        item.setBackgroundColor(QtGui.QColor(*item.note.color))
        if item.note.color not in [(255, 255, 255), [255, 255, 255], (202, 207, 210), [202, 207, 210]]:
            item.setForeground(QtGui.QColor("#FFFFFF"))
        else:
            item.setForeground(QtGui.QColor(*(0, 0, 0)))

        item.set_background_color()

    def color_notes(self):
        """
        Color all the notes of the listWidget
        """
        for i in range(0, self.lw_notes.count()):
            item = self.lw_notes.item(i)
            self.color_changer(item)

    def create_note(self):
        """
            Creating note with a title then saving it
        """
        title, resultat = QtWidgets.QInputDialog.getText(self,
                                                         "Ajouter une note", "Titre: ",
                                                         echo=QtWidgets.QLineEdit.Normal)
        if resultat and title:
            note = Note(title=title, color=(71, 166, 229))
            note.save()
            self.add_note_to_listwidget(note)
            self.color_notes()
            last_row = self.lw_notes.count()
            self.lw_notes.setCurrentItem(self.lw_notes.item(last_row-1))
            self.populate_note_content()

    def delete_selected_note(self):
        """
            Deleting the selected note with a dialog box
        """
        selected_item = self.get_selected_lw_item()
        self.confirmationBox.exec_()

        if selected_item and self.confirmationBox.clickedButton() == self.btn_yes:
            resultat = selected_item.note.delete()
            if resultat:
                self.lw_notes.takeItem(self.lw_notes.row(selected_item))
                # Pour enlever l'item de la liste directement (mise a jour visuelle, il n'existe déjà plus)

    def eventFilter(self, source, event):  # source = ou l'événement a eu lieu, event = l'evenement qui a eu lieu
        """
            Action to realize when a specific event happens in a specific location (source)
        :param source:
        :param event:
        :return:
        """
        if event.type() == QtCore.QEvent.ContextMenu and source is self.lw_notes:
            # Cette ligne veut dire que si le clique est reconnu comme une demande de contextmenu
            # et il vient de self.lw_notes, alors il se passera la suite

            selected_item = self.get_selected_lw_item()
            if selected_item:
                self.rc_menu.exec_(event.globalPos())  # Le menu s'ouvre à la position du clique
                return True
        return super().eventFilter(source, event)

    def get_selected_lw_item(self):
        """
            Returns the item that was selected else, returns None
        :return:
        """
        selected_items = self.lw_notes.selectedItems()
        if selected_items:
            return selected_items[0]
        return None

    def populate_notes(self):
        """
            Updates the list of notes
        """
        notes = get_notes()
        for note in notes:
            self.add_note_to_listwidget(note)
        self.color_notes()

    def populate_note_content(self):
        """
            Updates the note content window with the selected note content
        """
        try:
            selected_item = self.get_selected_lw_item()
            if selected_item:
                self.te_contenu.setText(selected_item.note.content)
                self.te_contenu.setFocus()
                cursor = QtGui.QTextCursor(self.te_contenu.document())
                cursor.setPosition(len(self.te_contenu.toPlainText()))
                self.te_contenu.setTextCursor(cursor)
                selected_item.set_background_color()
            else:
                self.te_contenu.clear()

        except Exception as e:
            self.fatal_error_message.setInformativeText(f"{e}")
            self.fatal_error_message.show()
            self.destroy()

    def rename_note(self):
        selected_item = self.get_selected_lw_item()
        row = self.lw_notes.currentRow()
        title, resultat = QtWidgets.QInputDialog.getText(self,
                                                         "Renommer la note", "Titre: ",
                                                         echo=QtWidgets.QLineEdit.Normal)
        if resultat and title:
            selected_item.note.title = title
            selected_item.note.save()
            self.lw_notes.clear()
            self.populate_notes()
            self.lw_notes.setCurrentItem(self.lw_notes.item(row))
            self.populate_note_content()

    def save_note(self):
        """
            Saves the note in the HD
        """
        selected_item = self.get_selected_lw_item()
        if selected_item:
            selected_item.note.content = self.te_contenu.toPlainText()  # On récupère le texte dans le textEditWidget
            # et on le met en tant que contenu de la note
            selected_item.note.save()

    def save_notes(self):
        """
            Saves all the notes
        """
        self.change_notes_order()
        for i in range(0, self.lw_notes.count()):
            self.lw_notes.item(i).note.save()

    def closeEvent(self, event):
        """
            Select the actions to be done when closing the app
        :param event:
        """
        self.save_notes()
