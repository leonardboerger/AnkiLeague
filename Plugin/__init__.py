from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import datetime
import uuid
from collections import defaultdict
import requests
from threading import Thread

class AnkiLeague:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        
        # Konfiguration laden und migrieren
        self.config = self.load_config()
        self.initialize_config()
        
        # Automatische Registrierung bei fehlendem Benutzernamen
        if not self.username:
            self.show_username_dialog(force=True)
        
        self.create_menu_items()

    def load_config(self):
        """Lädt und migriert alte Konfigurationsformate"""
        config = mw.addonManager.getConfig(__name__) or {}
        
        # Migration für alte Konfigurationsstruktur
        if 'config' in config:
            migrated_config = config['config']
            mw.addonManager.writeConfig(__name__, migrated_config)
            return migrated_config
        
        return config

    @property
    def user_id(self):
        return self.config['user_id']

    @property
    def username(self):
        return self.config['username']

    def initialize_config(self):
        """Initialisiert fehlende Konfigurationswerte"""
        defaults = {
            'user_id': str(uuid.uuid4()),
            'username': '',
            'synced_dates': []
        }
        needs_save = False
        for key, value in defaults.items():
            if key not in self.config or self.config[key] == '':
                self.config[key] = value
                needs_save = True
                
        if needs_save:
            self.save_config()

    def save_config(self):
        """Speichert die Konfiguration mit Fehlerbehandlung"""
        try:
            mw.addonManager.writeConfig(__name__, self.config)
        except Exception as e:
            showInfo(f"Konfigurationsfehler: {str(e)}")

    def set_username(self, new_username):
        """Setzt einen neuen Benutzernamen mit Validierung"""
        if new_username.strip():
            self.config['username'] = new_username.strip()
            self.save_config()
            return True
        return False

    def show_username_dialog(self, force=False):
        """Zeigt den Benutzernamen-Dialog an"""
        if not force and self.username:
            return
        
        dialog = QDialog(mw)
        dialog.setWindowTitle("AnkiLeague Registrierung")
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Bitte wählen Sie einen Benutzernamen:"))
        
        textbox = QLineEdit()
        textbox.setPlaceholderText("Benutzername")
        textbox.setText(self.username)
        layout.addWidget(textbox)
        
        buttons = QDialogButtonBox()
        ok_button = buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        
        def handle_submit():
            if self.set_username(textbox.text()):
                dialog.accept()
                showInfo("Benutzername erfolgreich gespeichert!")
            else:
                showInfo("Ungültiger Benutzername - mindestens 1 Zeichen erforderlich.")
        
        ok_button.clicked.connect(handle_submit)
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()

    def create_menu_items(self):
        """Erstellt die Menüeinträge"""
        # Sync-Action
        sync_action = QAction("AnkiLeague Synchronisieren", mw)
        qconnect(sync_action.triggered, self.sync_thread)
        mw.form.menuTools.addAction(sync_action)
        
        # Benutzername ändern
        change_action = QAction("AnkiLeague Benutzername ändern", mw)
        qconnect(change_action.triggered, lambda: self.show_username_dialog(force=True))
        mw.form.menuTools.addAction(change_action)

    def calculate_daily_stats(self):
        """Berechnet die täglichen Lernstatistiken"""
        revlogs = mw.col.db.all("SELECT id, ease, time FROM revlog") or []
        daily_stats = defaultdict(lambda: {'reviews': 0, 'successful': 0, 'time': 0})
        
        for log in revlogs:
            try:
                date = datetime.datetime.fromtimestamp(log[0] // 1000).date()
                daily_stats[date]['reviews'] += 1
                if log[1] > 1:  # Erfolgreiche Wiederholung
                    daily_stats[date]['successful'] += 1
                daily_stats[date]['time'] += log[2] // 1000  # Sekunden
            except Exception as e:
                print(f"Fehler bei Revlog-Verarbeitung: {str(e)}")
        
        return daily_stats

    def calculate_streaks(self, dates):
        """Berechnet die Lernserien (Streaks)"""
        sorted_dates = sorted(dates)
        streaks = {}
        current_streak = 0
        prev_date = None
        
        for date in sorted_dates:
            if prev_date and (date - prev_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            streaks[date] = current_streak
            prev_date = date
        
        return streaks

    def send_stats(self):
        """Sendet die Statistiken an den Server"""
        if not self.username:
            showInfo("Bitte zuerst einen Benutzernamen festlegen!")
            return

        try:
            daily_stats = self.calculate_daily_stats()
            dates = list(daily_stats.keys())
            streaks = self.calculate_streaks(dates)
            synced_dates = set(self.config.get('synced_dates', []))
            unsynced = [date for date in dates if str(date) not in synced_dates]

            if len(unsynced) == 0:
                unsynced = dates[-1:]  # Letzten Tag synchronisieren

            stats_list = []
            for date in unsynced:
                stats = daily_stats[date]
                try:
                    retention = (stats['successful'] / stats['reviews'] * 100) if stats['reviews'] > 0 else 0
                except ZeroDivisionError:
                    retention = 0
                
                stats_list.append({
                    'date': str(date),
                    'reviews': stats['reviews'],
                    'time': stats['time'],
                    'streak': streaks.get(date, 0),
                    'retention': round(retention, 2)
                })

            if not stats_list:
                showInfo("Keine neuen Daten zum Synchronisieren")
                return

            response = requests.post(
                'http://localhost:7999/data_manager/submitdata/',
                json={
                    'anki_uid': self.user_id,
                    'name': self.username,
                    'data': stats_list
                },
                timeout=15
            )
            
            if response.ok:
                self.config['synced_dates'] = list(synced_dates.union(map(str, unsynced)))
                self.save_config()
                # Info(f"Erfolgreich synchronisiert: {len(unsynced)} Tage")
            else:
                showInfo(f"Serverfehler: {response.status_code}\n{response.text}")
                
        except Exception as e:
            showInfo(f"Synchronisationsfehler: {str(e)}")

    def sync_thread(self):
        """Startet die Synchronisation"""
        self.send_stats()

def on_sync_finished():
    # showInfo("Synchronisation abgeschlossen")
    if hasattr(mw, 'ankileague'):
        mw.ankileague.sync_thread()
gui_hooks.sync_did_finish.append(on_sync_finished)
# Initialisierung
if not hasattr(mw, 'ankileague'):
    mw.ankileague = AnkiLeague()