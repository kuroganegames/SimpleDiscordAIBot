import sqlite3

class ChatLog:
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_table()

    # テーブルの作成
    def create_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                msg_id INTEGER PRIMARY KEY,
                msg_content TEXT,
                author TEXT,
                author_id INTEGER,
                channel TEXT,
                channel_id INTEGER,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    # メッセージの追加
    def add_message(self, msg_id, msg_content, author, author_id, channel, channel_id, timestamp):
        timestamp_str = timestamp.isoformat()
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            INSERT INTO messages (msg_id, msg_content, author, author_id, channel, channel_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (msg_id, msg_content, author, author_id, channel, channel_id, timestamp_str))
        conn.commit()
        conn.close()

    # メッセージの取得
    def get_message(self, msg_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM messages WHERE msg_id=?", (msg_id,))
        message = c.fetchone()
        conn.close()
        return message
    
    # 最新のメッセージを取得
    def get_latest_messages(self, channel_id, count=10):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM messages 
            WHERE channel_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (channel_id, count))
        messages = c.fetchall()
        conn.close()
        return messages
    
    # メッセージ内容の更新
    def update_message_content(self, msg_id, new_content):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            UPDATE messages 
            SET msg_content = ? 
            WHERE msg_id = ?
        ''', (new_content, msg_id))
        conn.commit()
        conn.close()