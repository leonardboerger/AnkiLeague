from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import datetime
import uuid
import json
from collections import defaultdict
import requests
from threading import Thread

# Initialisiere die Konfiguration, falls sie nicht existiert
config = mw.addonManager.getConfig(__name__)
if config is None:
    config = {}
    mw.addonManager.writeConfig(__name__, config)

# Setze eine Benutzer-ID, falls noch keine vorhanden ist
if 'user_id' not in config:
    config['user_id'] = str(uuid.uuid4())
    mw.addonManager.writeConfig(__name__, config)

def get_username():
    return config.get('username', '')

def set_username(new_username):
    config['username'] = new_username
    mw.addonManager.writeConfig(__name__, config)

def show_username_dialog():
    dialog = QDialog(mw)
    dialog.setWindowTitle("AnkiLeague Username")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Username:"))
    textbox = QLineEdit()
    textbox.setText(get_username())
    layout.addWidget(textbox)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(lambda: save_username(dialog, textbox.text()))
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    dialog.setLayout(layout)
    dialog.exec()

def save_username(dialog, username):
    set_username(username.strip())
    dialog.accept()

action = QAction("Set AnkiLeague Username", mw)
qconnect(action.triggered, show_username_dialog)
mw.form.menuTools.addAction(action)

def calculate_daily_stats():
    revlogs = mw.col.db.all("SELECT id, ease, time FROM revlog")
    daily_stats = defaultdict(lambda: {'reviews': 0, 'successful': 0, 'time': 0})
    for log in revlogs:
        date = datetime.datetime.fromtimestamp(log[0] // 1000).date()
        daily_stats[date]['reviews'] += 1
        if log[1] > 1:
            daily_stats[date]['successful'] += 1
        daily_stats[date]['time'] += log[2] // 1000  # Sekunden
    return daily_stats

def calculate_streaks(dates):
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

def send_stats():
    user_id = config['user_id']
    username = get_username()
    if not username:
        showInfo("Bitte Username setzen!")
        return

    daily_stats = calculate_daily_stats()
    dates = list(daily_stats.keys())
    streaks = calculate_streaks(dates)
    synced_dates = set(config.get('synced_dates', []))
    unsynced = [date for date in dates if str(date) not in synced_dates]

    stats_list = []
    for date in unsynced:
        stats = daily_stats[date]
        stats_list.append({
            'date': str(date),
            'reviews': stats['reviews'],
            'successful': stats['successful'],
            'time': stats['time'],
            'streak': streaks.get(date, 0)
        })

    if not stats_list:
        return

    try:
        response = requests.post(
            'http://localhost:8000/api/submit-stats/',
            json={
                'user_id': user_id,
                'username': username,
                'stats': stats_list
            },
            timeout=10
        )
        if response.ok:
            config['synced_dates'] = list(synced_dates.union(map(str, unsynced)))
            mw.addonManager.writeConfig(__name__, config)
            showInfo(f"{len(unsynced)} Tage synchronisiert!")
        else:
            showInfo("Fehler beim Synchronisieren: " + response.text)
    except Exception as e:
        showInfo("Fehler: " + str(e))

def anzeigen():
    user_id = config['user_id']
    username = get_username()
    if not username:
        showInfo("Bitte Username setzen!")
        return

    daily_stats = calculate_daily_stats()
    dates = list(daily_stats.keys())
    streaks = calculate_streaks(dates)
    synced_dates = set(config.get('synced_dates', []))
    unsynced = [date for date in dates if str(date) not in synced_dates]

    stats_list = []
    for date in unsynced:
        stats = daily_stats[date]
        stats_list.append({
            'date': str(date),
            'reviews': stats['reviews'],
            'successful': stats['successful'],
            'time': stats['time'],
            'streak': streaks.get(date, 0)
        })
    index = -2
    showInfo(f"{stats_list[index]['date']}, {stats_list[index]['reviews']}, {stats_list[index]['successful']}, {stats_list[index]['time']}, {stats_list[index]['streak']}")

# create a new menu item, "test"
anzeigen_action = QAction("test", mw)
qconnect(anzeigen_action.triggered, anzeigen)
mw.form.menuTools.addAction(anzeigen_action)

def sync_thread():
    thread = Thread(target=send_stats)
    thread.start()

sync_action = QAction("Sync AnkiLeague", mw)
qconnect(sync_action.triggered, sync_thread)
mw.form.menuTools.addAction(sync_action)