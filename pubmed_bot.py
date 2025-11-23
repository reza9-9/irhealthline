import requests
import json
from datetime import datetime
import time
import re

class PubMedBot:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.searches_today = 0
        self.max_searches_per_day = 10  # محدودیت استفاده
        
    def search_meta_analysis(self, topic):
        """جستجوی متا-آنالیز از PubMed"""
        try:
            if self.searches_today >= self.max_searches_per_day:
                print("⚠️ محدودیت استفاده روزانه از PubMed رسیده")
                return None
                
            print(f"🔍 در حال جستجوی متا-آنالیز برای: {topic}")
            
            # جستجو در PubMed
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'({topic}) AND (meta-analysis[pt] OR systematic review[pt])',
                'retmax': 3,  # فقط ۳ مقاله
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            self.searches_today += 1
            
            if response.status_code == 200:
                data = response.json()
                article_ids = data.get('esearchresult', {}).get('idlist', [])
                
                if article_ids:
                    print(f"✅ {len(article_ids)} مقاله پیدا شد")
                    return self.get_article_details(article_ids)
                else:
                    print("📭 هیچ مقاله‌ای پیدا نشد")
                    return None
                    
            else:
                print(f"❌ خطا در جستجوی PubMed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ خطا در اتصال به PubMed: {e}")
            return None
    
    def get_article_details(self, article_ids):
        """دریافت جزئیات مقالات"""
        try:
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(article_ids),
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return self.parse_articles_xml(response.text)
            else:
                print(f"❌ خطا در دریافت جزئیات: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ خطا در پردازش مقالات: {e}")
            return None
    
    def parse_articles_xml(self, xml_content):
        """پردازش XML مقالات"""
        try:
            import xml.etree.ElementTree as ET
            
            articles = []
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                # عنوان مقاله
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None else "بدون عنوان"
                
                # چکیده مقاله
                abstract_elem = article.find('.//AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else "چکیده موجود نیست"
                
                # نویسندگان
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.find('LastName')
                    fore_name = author.find('ForeName')
                    if last_name is not None and fore_name is not None:
                        authors.append(f"{fore_name.text} {last_name.text}")
                
                # سال انتشار
                pub_date_elem = article.find('.//PubDate/Year')
                pub_year = pub_date_elem.text if pub_date_elem is not None else "نامشخص"
                
                articles.append({
                    'title': title,
                    'abstract': abstract[:500] + "..." if len(abstract) > 500 else abstract,  # محدودیت طول
                    'authors': authors[:3],  # فقط ۳ نویسنده اول
                    'year': pub_year,
                    'source': 'PubMed'
                })
            
            return articles
            
        except Exception as e:
            print(f"❌ خطا در پردازش XML: {e}")
            return None
    
    def generate_summary(self, topic, articles):
        """تولید خلاصه از مقالات"""
        if not articles:
            return None
            
        print(f"📝 در حال تولید خلاصه برای {topic}...")
        
        summary = f"بر اساس {len(articles)} مطالعه متا-آنالیز از PubMed:\n\n"
        
        for i, article in enumerate(articles, 1):
            summary += f"📄 مطالعه {i}:\n"
            summary += f"   عنوان: {article['title']}\n"
            summary += f"   نویسندگان: {', '.join(article['authors']) if article['authors'] else 'نامشخص'}\n"
            summary += f"   سال: {article['year']}\n"
            summary += f"   خلاصه: {article['abstract']}\n\n"
        
        # نکات کلیدی
        summary += "💡 نکات کلیدی:\n"
        summary += "• این مطالعات بر اساس شواهد علمی معتبر انجام شده‌اند\n"
        summary += "• متا-آنالیزها معتبرترین سطح شواهد پزشکی هستند\n"
        summary += "• برای اطلاعات بیشتر با پزشک خود مشورت کنید\n"
        
        return summary

def main():
    """تست ربات PubMed"""
    print("🧪 تست ربات PubMed...")
    bot = PubMedBot()
    
    # تست با یک موضوع
    topic = "diabetes treatment"
    articles = bot.search_meta_analysis(topic)
    
    if articles:
        summary = bot.generate_summary(topic, articles)
        print(f"\n📊 خلاصه تولید شده:\n{summary}")
    else:
        print("❌ هیچ مقاله‌ای یافت نشد")

if __name__ == "__main__":
    main()
