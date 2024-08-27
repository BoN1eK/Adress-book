import sys
import json
import sqlite3
import warnings
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QHeaderView, QInputDialog)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

# Wyłączenie ostrzeżeń o deprecjonowaniu
warnings.filterwarnings("ignore", category=DeprecationWarning)

class AddressBook(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()
        self.loadData()

    def initUI(self):
        self.setWindowTitle('Książka Adresowa')
        self.setGeometry(100, 100, 800, 400)

        # Ustawienie tła
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(230, 230, 250))  # Ustawienie koloru tła na błękitny
        self.setPalette(p)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Tytuł
        title = QLabel('Książka Adresowa', self)
        title.setFont(QFont('Arial', 24))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Formularz do wprowadzania danych
        form_layout = QHBoxLayout()
        self.first_name_input = QLineEdit(self)
        self.first_name_input.setPlaceholderText("Imię")
        form_layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit(self)
        self.last_name_input.setPlaceholderText("Nazwisko")
        form_layout.addWidget(self.last_name_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Numer telefonu")
        form_layout.addWidget(self.phone_input)

        self.address_input = QLineEdit(self)
        self.address_input.setPlaceholderText("Adres")
        form_layout.addWidget(self.address_input)

        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Miasto")
        form_layout.addWidget(self.city_input)

        main_layout.addLayout(form_layout)

        # Przyciski
        button_layout = QHBoxLayout()
        button_colors = ["lightgreen", "lightblue", "lightyellow", "lightcoral"]
        button_texts = ["Dodaj", "Szukaj", "Statystyki", "Usuń"]
        button_functions = [self.addEntry, self.searchEntry, self.showStats, self.deleteEntry]

        for i, color in enumerate(button_colors):
            button = QPushButton(button_texts[i], self)
            button.setStyleSheet(f"background-color: {color}; font-weight: bold;")
            button.clicked.connect(button_functions[i])
            button_layout.addWidget(button)
        main_layout.addLayout(button_layout)

        # Tabela do wyświetlania danych
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Imię", "Nazwisko", "Numer telefonu", "Adres", "Miasto"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        main_layout.addWidget(self.table)

    def initDB(self):
        self.conn = sqlite3.connect('address_book.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS addresses
                          (first_name TEXT, last_name TEXT, phone TEXT, address TEXT, city TEXT)''')
        self.conn.commit()

    def loadData(self):
        try:
            with open('address_book.json', 'r') as file:
                self.address_data = json.load(file)
        except FileNotFoundError:
            QMessageBox.warning(self, "Błąd", "Plik z danymi nie istnieje!")
            self.address_data = []
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Błąd", "Błąd dekodowania danych JSON!")
            self.address_data = []

        self.updateTable(self.address_data)

    def saveData(self):
        try:
            with open('address_book.json', 'w') as file:
                json.dump(self.address_data, file)
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Wystąpił błąd podczas zapisu danych: {e}")

    def updateTable(self, data):
        self.table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(entry['first_name']))
            self.table.setItem(row, 1, QTableWidgetItem(entry['last_name']))
            self.table.setItem(row, 2, QTableWidgetItem(entry['phone']))
            self.table.setItem(row, 3, QTableWidgetItem(entry['address']))
            self.table.setItem(row, 4, QTableWidgetItem(entry['city']))

    def addEntry(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        city = self.city_input.text()

        if not first_name or not last_name:
            QMessageBox.warning(self, "Błąd", "Imię i nazwisko są wymagane!")
            return

        for entry in self.address_data:
            if (entry['first_name'].lower() == first_name.lower() and entry['last_name'].lower() == last_name.lower()):
                QMessageBox.warning(self, "Błąd", "Osoba o takim imieniu i nazwisku juz istnieje!")
                return
            elif entry['phone'] == phone:
                QMessageBox.warning(self, "Błąd", "Osoba o takim numerze telefonu juz istnieje!")
                return

        new_entry = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "address": address,
            "city": city
        }

        self.address_data.append(new_entry)
        self.saveData()
        self.updateTable(self.address_data)
        self.clearInputs()

    def searchEntry(self):
        search_first_name = self.first_name_input.text().lower()
        search_last_name = self.last_name_input.text().lower()
        search_phone = self.phone_input.text().lower()
        search_address = self.address_input.text().lower()
        search_city = self.city_input.text().lower()

        filtered_data = [
            entry for entry in self.address_data
            if (search_first_name in entry['first_name'].lower() or not search_first_name) and
               (search_last_name in entry['last_name'].lower() or not search_last_name) and
               (search_phone in entry['phone'].lower() or not search_phone) and
               (search_address in entry['address'].lower() or not search_address) and
               (search_city in entry['city'].lower() or not search_city)
        ]

        self.updateTable(filtered_data)

    def showStats(self):
        search_first_name = self.first_name_input.text().lower()
        search_last_name = self.last_name_input.text().lower()
        search_phone = self.phone_input.text().lower()
        search_address = self.address_input.text().lower()
        search_city = self.city_input.text().lower()


        filtered_data = [
            entry for entry in self.address_data
            if (search_first_name in entry['first_name'].lower() or not search_first_name) and
               (search_last_name in entry['last_name'].lower() or not search_last_name) and
               (search_phone in entry['phone'].lower() or not search_phone) and
               (search_address in entry['address'].lower() or not search_address) and
               (search_city in entry['city'].lower() or not search_city)
        ]

        first_name_counts = {}
        last_name_counts = {}

        for entry in filtered_data:
            first_name = entry['first_name']
            last_name = entry['last_name']

            if first_name in first_name_counts:
                first_name_counts[first_name] +=1
            else:
                first_name_counts[first_name] = 1

            if last_name in last_name_counts:
                last_name_counts[last_name] += 1
            else:
                last_name_counts[last_name] = 1

        stats_message = "Statystyki:\n\n"

        if first_name_counts:
            stats_message += "Imiona:\n"
            for name, count in first_name_counts.items():
                stats_message += f"{name}: {count}\n"
        else:
            stats_message+="Brak wyników"
        stats_message +="\n"

        if last_name_counts:
            stats_message += "\nNazwiska:\n"
            for name, count in last_name_counts.items():
                stats_message += f"{name}: {count}\n"
        else:
            stats_message+="Brak wyników"

        QMessageBox.information(self, "Statystyki", stats_message)
    def deleteEntry(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Błąd", "Musisz wybrać wpis do usunięcia!")
            return

        first_name = self.table.item(selected_row, 0).text()
        last_name = self.table.item(selected_row, 1).text()
        phone = self.table.item(selected_row, 2).text()
        address = self.table.item(selected_row, 3).text()
        city = self.table.item(selected_row, 4).text()

        self.address_data = [
            entry for entry in self.address_data
            if not (entry['first_name'] == first_name and entry['last_name'] == last_name and
                    entry['phone'] == phone and entry['address'] == address and entry['city'] == city)
        ]
        self.saveData()
        self.updateTable(self.address_data)

    def clearInputs(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.city_input.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    address_book = AddressBook()
    address_book.show()
    sys.exit(app.exec_())
