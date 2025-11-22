import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class MedicalAnalytics:
    def __init__(self, db_path="medical_content.db"):
        self.db_path = db_path
    
    def generate_weekly_report(self):
        """تولید گزارش هفتگی"""
        print("📈 در حال تولید گزارش هفتگی...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # آمار هفته گذشته
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            weekly_stats = pd.read_sql_query('''
                SELECT 
                    COUNT(*) as total_articles,
                    SUM(word_count) as total_words,
                    AVG(quality_score) as avg_quality,
                    COUNT(DISTINCT category) as unique_categories
                FROM articles 
                WHERE DATE(created_at) >= ?
            ''', conn, params=[week_ago])
            
            conn.close()
            
            stats = weekly_stats.to_dict('records')[0] if not weekly_stats.empty else {
                'total_articles': 0,
                'total_words': 0,
                'avg_quality': 0,
                'unique_categories': 0
            }
            
            report = {
                "period": "هفتگی",
                "start_date": week_ago,
                "end_date": datetime.now().strftime('%Y-%m-%d'),
                "stats": stats,
                "generated_at": datetime.now().isoformat()
            }
            
            # ذخیره گزارش
            filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"✅ گزارش هفتگی تولید شد: {filename}")
            
            # نمایش خلاصه
            print(f"📊 خلاصه هفتگی:")
            print(f"   📄 مقالات: {stats['total_articles']}")
            print(f"   📝 کلمات: {stats['total_words']}")
            print(f"   ⭐ کیفیت: {stats['avg_quality']:.1f}/10")
            print(f"   🏷️ دسته‌بندی‌ها: {stats['unique_categories']}")
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش هفتگی: {e}")
            return {}

def main():
    """تابع اصلی برای تست آنالیز"""
    print("🎯 در حال تولید گزارش‌های آنالیز...")
    analytics = MedicalAnalytics()
    analytics.generate_weekly_report()

if __name__ == "__main__":
    main()
