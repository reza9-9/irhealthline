import sqlite3
import json
import pandas as pd
from datetime import datetime
import os

class MedicalDatabase:
    def __init__(self, db_path="medical_content.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """ایجاد جداول دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول مقالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                word_count INTEGER,
                reading_time TEXT,
                quality_score INTEGER,
                status TEXT DEFAULT 'تولید شده',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published BOOLEAN DEFAULT FALSE,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0
            )
        ''')
        
        # جدول آمار روزانه
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_articles INTEGER,
                total_words INTEGER,
                avg_quality REAL,
                categories_json TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ دیتابیس با موفقیت راه‌اندازی شد")
    
    def save_articles(self, articles):
        """ذخیره مقالات در دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for article in articles:
            cursor.execute('''
                INSERT INTO articles 
                (title, content, category, word_count, reading_time, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['title'],
                article['content'],
                article['category'],
                article['word_count'],
                article['reading_time'],
                article['quality_score'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(articles)} مقاله در دیتابیس ذخیره شد")
    
    def get_daily_stats(self):
        """دریافت آمار روزانه"""
        conn = sqlite3.connect(self.db_path)
        
        # آمار مقالات امروز
        today = datetime.now().strftime('%Y-%m-%d')
        df = pd.read_sql_query('''
            SELECT 
                COUNT(*) as total_articles,
                SUM(word_count) as total_words,
                AVG(quality_score) as avg_quality,
                GROUP_CONCAT(DISTINCT category) as categories
            FROM articles 
            WHERE DATE(created_at) = ?
        ''', conn, params=[today])
        
        conn.close()
        return df.to_dict('records')[0] if not df.empty else {}
