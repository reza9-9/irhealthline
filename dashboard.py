from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import json
import os

class MedicalDashboard:
    def __init__(self, db_path="medical_content.db"):
        self.db_path = db_path
    
    def get_overview_stats(self):
        """آمار کلی سیستم"""
        conn = sqlite3.connect(self.db_path)
        
        stats = {}
        
        try:
            # کل مقالات
            stats['total_articles'] = pd.read_sql_query(
                'SELECT COUNT(*) as count FROM articles', conn
            ).iloc[0]['count']
            
            # مقالات امروز
            today = datetime.now().strftime('%Y-%m-%d')
            stats['today_articles'] = pd.read_sql_query(
                'SELECT COUNT(*) as count FROM articles WHERE DATE(created_at) = ?', 
                conn, params=[today]
            ).iloc[0]['count']
            
            # میانگین کیفیت
            stats['avg_quality'] = pd.read_sql_query(
                'SELECT AVG(quality_score) as avg FROM articles', conn
            ).iloc[0]['avg']
            
            # توزیع دسته‌بندی‌ها
            stats['categories'] = pd.read_sql_query('''
                SELECT category, COUNT(*) as count 
                FROM articles 
                GROUP BY category 
                ORDER BY count DESC
            ''', conn).to_dict('records')
            
            # کل کلمات تولید شده
            stats['total_words'] = pd.read_sql_query(
                'SELECT SUM(word_count) as total FROM articles', conn
            ).iloc[0]['total'] or 0
            
        except Exception as e:
            print(f"❌ خطا در دریافت آمار: {e}")
            stats = {
                'total_articles': 0,
                'today_articles': 0,
                'avg_quality': 0,
                'categories': [],
                'total_words': 0
            }
        
        conn.close()
        return stats
    
    def get_weekly_report(self):
        """گزارش هفتگی"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # آمار ۷ روز گذشته
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            weekly_stats = pd.read_sql_query('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as article_count,
                    SUM(word_count) as total_words,
                    AVG(quality_score) as avg_quality
                FROM articles 
                WHERE DATE(created_at) >= ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            ''', conn, params=[week_ago])
            
            result = weekly_stats.to_dict('records')
        except Exception as e:
            print(f"❌ خطا در دریافت گزارش هفتگی: {e}")
            result = []
        
        conn.close()
        return result
    
    def generate_html_dashboard(self):
        """تولید داشبورد HTML"""
        stats = self.get_overview_stats()
        weekly = self.get_weekly_report()
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>داشبورد مدیریت محتوای پزشکی</title>
            <style>
                body {{ font-family: Tahoma, Arial; background: #f0f8ff; margin: 0; padding: 20px; }}
                .dashboard {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #2c5aa0, #1e3a8a); color: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.2); }}
                .stat-number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }}
                .stat-label {{ font-size: 1.1em; opacity: 0.9; }}
                h1 {{ color: #2c5aa0; text-align: center; margin-bottom: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: center; border: 1px solid #ddd; }}
                th {{ background: #2c5aa0; color: white; }}
                tr:nth-child(even) {{ background: #f8f9fa; }}
                .last-update {{ text-align: center; color: #666; margin-top: 30px; font-style: italic; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h1>🏥 داشبورد مدیریت محتوای پزشکی</h1>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_articles']}</div>
                        <div class="stat-label">📊 کل مقالات</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['today_articles']}</div>
                        <div class="stat-label">📅 مقالات امروز</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['avg_quality']:.1f}/10</div>
                        <div class="stat-label">⭐ میانگین کیفیت</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_words']}</div>
                        <div class="stat-label">📝 کل کلمات</div>
                    </div>
                </div>
                
                <h2>📈 گزارش هفتگی عملکرد</h2>
                <table>
                    <tr>
                        <th>📅 تاریخ</th>
                        <th>📄 تعداد مقالات</th>
                        <th>📊 کل کلمات</th>
                        <th>⭐ میانگین کیفیت</th>
                    </tr>
        """
        
        if weekly:
            for day in weekly:
                html += f"""
                    <tr>
                        <td>{day['date']}</td>
                        <td>{day['article_count']}</td>
                        <td>{day['total_words']}</td>
                        <td>{day['avg_quality']:.1f}/10</td>
                    </tr>
                """
        else:
            html += """
                    <tr>
                        <td colspan="4" style="text-align: center; padding: 20px;">
                            📭 هیچ داده‌ای برای نمایش وجود ندارد
                        </td>
                    </tr>
            """
        
        html += f"""
                </table>
                
                <h2>🏷️ توزیع موضوعات</h2>
                <table>
                    <tr>
                        <th>دسته‌بندی</th>
                        <th>تعداد مقالات</th>
                    </tr>
        """
        
        if stats['categories']:
            for category in stats['categories']:
                html += f"""
                    <tr>
                        <td>{category['category']}</td>
                        <td>{category['count']}</td>
                    </tr>
                """
        else:
            html += """
                    <tr>
                        <td colspan="2" style="text-align: center; padding: 20px;">
                            📭 هیچ دسته‌بندی‌ای وجود ندارد
                        </td>
                    </tr>
            """
        
        html += f"""
                </table>
                
                <div class="last-update">
                    آخرین بروزرسانی: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        
        # ذخیره فایل HTML
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ داشبورد HTML ایجاد شد: index.html")
        return html

def main():
    """تابع اصلی برای تست داشبورد"""
    print("🎯 در حال تولید داشبورد مدیریت...")
    dashboard = MedicalDashboard()
    dashboard.generate_html_dashboard()
    print("✅ داشبورد با موفقیت ایجاد شد")

if __name__ == "__main__":
    main()
