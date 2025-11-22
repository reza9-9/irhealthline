import requests
import json
from datetime import datetime
import os
import time

class WebsiteAutoPoster:
    def __init__(self, website_url=None, api_key=None):
        self.website_url = website_url or os.environ.get('WEBSITE_URL', '')
        self.api_key = api_key or os.environ.get('WEBSITE_API_KEY', '')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def post_to_website(self, article):
        """ارسال مقاله به وبسایت"""
        try:
            print(f"🌐 در حال ارسال مقاله به وبسایت: {article['title']}")
            
            # اگر کلید API تنظیم نشده، فقط شبیه‌سازی کن
            if not self.api_key or not self.website_url:
                print("⚠️ کلید وبسایت تنظیم نشده - شبیه‌سازی ارسال")
                time.sleep(1)
                return True
            
            payload = {
                'title': article['title'],
                'content': article['content'],
                'category': article['category'],
                'meta_description': f"مقاله پزشکی درباره {article['title']}",
                'tags': ['پزشکی', 'سلامت', article['category']],
                'status': 'publish'
            }
            
            response = requests.post(
                f"{self.website_url}/wp-json/wp/v2/posts",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                print(f"✅ مقاله '{article['title']}' در وبسایت منتشر شد")
                return True
            else:
                print(f"❌ خطا در انتشار: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در ارسال به وبسایت: {e}")
            return False
    
    def post_multiple_articles(self, articles):
        """ارسال چندین مقاله به وبسایت"""
        print(f"\n🚀 شروع ارسال {len(articles)} مقاله به وبسایت...")
        results = []
        for i, article in enumerate(articles, 1):
            print(f"📤 ارسال مقاله {i}/{len(articles)}: {article['title']}")
            result = self.post_to_website(article)
            results.append({
                'title': article['title'],
                'success': result,
                'timestamp': datetime.now().isoformat()
            })
            time.sleep(2)  # تأخیر بین ارسال‌ها
        
        success_count = sum(1 for r in results if r['success'])
        print(f"📊 نتایج ارسال: {success_count}/{len(articles)} موفق")
        return results
