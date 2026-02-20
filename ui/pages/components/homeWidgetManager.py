import pickle
import uuid
from modules.database.database import cursor, connection

_TABLE = 'HomepageWidgetsTable'


def _ensure_table():
    # create the table if it doesn't exist — mirrors other page cache patterns
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {_TABLE} (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            data BLOB
        )
    ''')
    connection.commit()


def load_widget_list() -> list[dict]:
    _ensure_table()
    try:
        cursor.execute(f'SELECT data FROM {_TABLE} WHERE id = 1')
        row = cursor.fetchone()
        if row:
            return pickle.loads(row[0])
    except Exception as e:
        print(f'homeWidgetManager load error: {e}')
    return []


def save_widget_list(widget_list: list[dict]):
    _ensure_table()
    try:
        data = pickle.dumps(widget_list)
        cursor.execute(
            f'INSERT OR REPLACE INTO {_TABLE} (id, data) VALUES (1, ?)',
            (data,)
        )
        connection.commit()
    except Exception as e:
        print(f'homeWidgetManager save error: {e}')


def add_widget(widget_type: str, config: dict) -> str:
    # append a new widget record to the stored list and return its id
    widgets = load_widget_list()
    widget_id = str(uuid.uuid4())[:8]
    widgets.append({'widget_id': widget_id, 'widget_type': widget_type, 'config': config})
    save_widget_list(widgets)
    return widget_id
