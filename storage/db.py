import sqlite3
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/pulse_production.db"):
        self.db_path = db_path
        self.sqlite3 = sqlite3
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Raw Reviews
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS raw_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT,
                    rating INTEGER,
                    review_text TEXT,
                    review_date TEXT,
                    content_hash TEXT UNIQUE,
                    created_at TEXT
                )
            ''')
            # Filtered Reviews
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS filtered_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT,
                    review_text TEXT,
                    rating INTEGER,
                    review_date TEXT,
                    processed_at TEXT,
                    sentiment TEXT,
                    category TEXT,
                    platform TEXT,
                    app_version TEXT,
                    helpful_count INTEGER DEFAULT 0,
                    assigned_to TEXT,
                    content_hash TEXT UNIQUE
                )
            ''')

            # Reports Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary TEXT,
                    themes TEXT,
                    quotes TEXT,
                    action_items TEXT,
                    fee_scenarios TEXT,
                    email_subject TEXT,
                    email_body TEXT,
                    json_path TEXT,
                    pdf_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    review_count INTEGER
                )
            ''')
            conn.commit()

    def save_raw_reviews(self, reviews):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for r in reviews:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO raw_reviews (platform, rating, review_text, review_date, content_hash, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (r.get('platform'), r.get('rating'), r['review_text'], r.get('date'), r.get('hash'), datetime.now().isoformat()))
                except:
                    continue
            conn.commit()

    def save_report(self, report_data, review_count, json_path=None, pdf_path=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            pulse = report_data.get('weekly_pulse', {})
            email = report_data.get('email_draft', {})
            
            cursor.execute('''
                INSERT INTO reports (
                    summary, themes, quotes, action_items, fee_scenarios, 
                    email_subject, email_body, json_path, pdf_path, created_at, review_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pulse.get('summary'),
                json.dumps(pulse.get('themes', [])),
                json.dumps(pulse.get('quotes', [])),
                json.dumps(pulse.get('action_items', [])),
                json.dumps(report_data.get('fee_scenarios', [])),
                email.get('subject'),
                email.get('body'),
                json_path,
                pdf_path,
                datetime.now().isoformat(),
                review_count
            ))
            report_id = cursor.lastrowid
            conn.commit()
            return report_id

    def save_filtered_reviews(self, reviews):
        """
        Inserts or updates filtered reviews based on content_hash.
        """
        import hashlib
        with self._get_connection() as conn:
            cursor = conn.cursor()
            count = 0
            for r in reviews:
                # Generate hash if missing
                if not r.get('content_hash'):
                    text_to_hash = f"{r['review_text']}_{r.get('platform', 'all')}"
                    r['content_hash'] = hashlib.md5(text_to_hash.encode()).hexdigest()
                
                try:
                    cursor.execute('''
                        INSERT INTO filtered_reviews (
                            user_name, review_text, rating, review_date, processed_at, 
                            sentiment, category, platform, app_version, helpful_count, content_hash
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(content_hash) DO UPDATE SET
                            user_name = excluded.user_name,
                            sentiment = excluded.sentiment,
                            category = excluded.category,
                            app_version = excluded.app_version,
                            helpful_count = excluded.helpful_count
                    ''', (
                        r.get('user_name'), r['review_text'], r['rating'], r.get('review_date') or r.get('date'), 
                        datetime.now().isoformat(), r.get('sentiment'), r.get('category'), 
                        r.get('platform'), r.get('app_version'), r.get('helpful_count', 0),
                        r['content_hash']
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error upserting review: {e}")
                    continue
            conn.commit()
            return count

    def get_all_reports(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_report_by_id(self, report_id):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['themes'] = json.loads(d['themes'])
                d['quotes'] = json.loads(d['quotes'])
                d['action_items'] = json.loads(d['action_items'])
                d['fee_scenarios'] = json.loads(d.get('fee_scenarios', '[]'))
                return d
            return None
