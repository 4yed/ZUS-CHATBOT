import sqlite3
import re
import logging
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutletDB:
    def __init__(self, db_path: str = 'zus_outlets.db'):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        cursor = self.connect().cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def init_db(self):
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS outlets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, address TEXT NOT NULL,
            city TEXT NOT NULL, state TEXT NOT NULL, services TEXT, hours TEXT,
            parking_available BOOLEAN DEFAULT 0, wifi_available BOOLEAN DEFAULT 0
        )
        """)
        # Check if outlets table is empty
        if not self.execute_query("SELECT * FROM outlets"):
            self.populate_sample_data()

    def populate_sample_data(self):
        outlets_data = [
            ("ZUS Coffee - Binjai 8 Premium SOHO", "G04, Pangsapuri Servis (Suite) Binjai 8 No, 2, Lorong Binjai",
             "Kuala Lumpur", "Kuala Lumpur", "coffee,food,wifi,parking,dine_in,takeaway", "07:00-22:00", 1, 1),
            ("ZUS Coffee - Atria Shopping Gallery", "C01A, Concourse Floor, Atria Shopping Gallery, Jalan SS 22/23, Damansara Jaya",
             "Petaling Jaya", "Selangor", "coffee,food,wifi,drive_thru,parking,dine_in,takeaway", "08:00-22:00", 1, 1),
        ]
        cursor = self.connect().cursor()
        cursor.executemany("INSERT INTO outlets (name, address, city, state, services, hours, parking_available, wifi_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", outlets_data)
        self.connect().commit()
        logger.info(f"Populated database with {len(outlets_data)} sample outlets")

class Text2SQL:
    def convert(self, query: str) -> str:
        query_lower = query.lower().strip()
        base_query = "SELECT name, address, hours, services FROM outlets"
        conditions = []

        if any(k in query_lower for k in ['kuala lumpur', 'kl']):
            conditions.append("city LIKE '%Kuala Lumpur%'")
        if any(k in query_lower for k in ['selangor', 'pj']):
            conditions.append("state LIKE '%Selangor%'")
        if 'parking' in query_lower:
            conditions.append("parking_available = 1")
        if 'wifi' in query_lower:
            conditions.append("wifi_available = 1")

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        return base_query + " LIMIT 10;"

class OutletQueryProcessor:
    def __init__(self, db_path: str = 'zus_outlets.db'):
        self.db = OutletDB(db_path)
        self.db.init_db()
        self.converter = Text2SQL()

    def process(self, natural_query: str) -> Dict[str, Any]:
        try:
            sql_query = self.converter.convert(natural_query)
            results = self.db.execute_query(sql_query)
            return {
                'sql_query': sql_query,
                'results': results,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {'success': False, 'error': str(e)} 