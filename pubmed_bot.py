import requests
import json
from datetime import datetime
import time
import re
import random
import xml.etree.ElementTree as ET

class PubMedBot:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.searches_today = 0
        self.max_searches_per_day = 100  # افزایش محدودیت
        self.email = "your-email@example.com"  # ضروری برای PubMed
        self.api_key = None  # اگر داری اضافه کن
        
    def search_meta_analysis(self, topic):
        """جستجوی متا-آنالیز از PubMed - نسخه تصحیح شده"""
        try:
            if self.searches_today >= self.max_searches_per_day:
                print("⚠️ محدودیت استفاده روزانه از PubMed رسیده")
                return None
                
            print(f"🔍 در حال جستجوی متا-آنالیز برای: {topic}")
            
            # جستجوی بهینه‌شده
            search_url = f"{self.base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': f'{topic} AND (meta-analysis[pt] OR systematic review[pt])',
                'retmax': 5,  # افزایش تعداد نتایج
                'retmode': 'json',
                'sort': 'relevance',
                'field': 'title,abstract',
                'datetype': 'pdat',
                'reldate': 3650,  # مقالات ۱۰ سال اخیر
                'email': self.email
            }
            
            # اضافه کردن API Key اگر موجود باشد
            if self.api_key:
                params['api_key'] = self.api_key
                
            print(f"📡 در حال ارسال درخواست به PubMed...")
            response = requests.get(search_url, params=params, timeout=30)
            self.searches_today += 1
            
            print(f"📊 وضعیت پاسخ: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                article_ids = data.get('esearchresult', {}).get('idlist', [])
                
                print(f"🔍 تعداد مقالات یافت شده: {len(article_ids)}")
                
                if article_ids:
                    print(f"✅ {len(article_ids)} مقاله پیدا شد")
                    article_details = self.get_article_details(article_ids)
                    if article_details:
                        return article_details
                    else:
                        print("❌ مشکل در دریافت جزئیات مقالات")
                        return None
                else:
                    print("📭 هیچ مقاله‌ای پیدا نشد - شاید کوئری مشکل دارد")
                    # نمایش خطای کامل برای دیباگ
                    print(f"📋 پاسخ کامل: {data}")
                    return None
                    
            else:
                print(f"❌ خطا در جستجوی PubMed: {response.status_code}")
                print(f"📄 متن خطا: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ timeout در اتصال به PubMed")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ خطای اتصال به اینترنت")
            return None
        except Exception as e:
            print(f"❌ خطای ناشناخته: {e}")
            return None
    
    def get_article_details(self, article_ids):
        """دریافت جزئیات کامل مقالات - نسخه بهبود یافته"""
        try:
            if not article_ids:
                return None
                
            fetch_url = f"{self.base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(article_ids),
                'retmode': 'xml',
                'rettype': 'abstract',
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
                
            print(f"📥 دریافت جزئیات {len(article_ids)} مقاله...")
            response = requests.get(fetch_url, params=params, timeout=45)
            
            if response.status_code == 200:
                articles = self.parse_complete_articles(response.text)
                if articles:
                    print(f"✅ موفقیت آمیز: {len(articles)} مقاله پردازش شد")
                    return articles
                else:
                    print("❌ مشکل در پردازش مقالات")
                    return None
            else:
                print(f"❌ خطا در دریافت جزئیات: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ خطا در پردازش مقالات: {e}")
            return None
    
    def parse_complete_articles(self, xml_content):
        """پردازش کامل مقالات - نسخه مقاوم به خطا"""
        try:
            articles = []
            
            # پاکسازی XML
            clean_xml = re.sub(r'xmlns="[^"]+"', '', xml_content)
            root = ET.fromstring(clean_xml)
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    # عنوان مقاله
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else "بدون عنوان"
                    
                    # چکیده کامل
                    abstract_text = ""
                    abstract_elems = article.findall('.//AbstractText')
                    for elem in abstract_elems:
                        if elem is not None and elem.text:
                            label = elem.get('Label', '')
                            if label:
                                abstract_text += f"{label}: {elem.text} "
                            else:
                                abstract_text += elem.text + " "
                    
                    abstract = abstract_text.strip() if abstract_text else "چکیده کامل موجود نیست"
                    
                    # فقط مقالات با چکیده کامل
                    if len(abstract) < 100:  # چکیده خیلی کوتاه
                        continue
                    
                    # نویسندگان
                    authors = []
                    for author in article.findall('.//Author'):
                        last_name = author.find('LastName')
                        fore_name = author.find('ForeName')
                        if last_name is not None and last_name.text:
                            full_name = last_name.text
                            if fore_name is not None and fore_name.text:
                                full_name = f"{fore_name.text} {full_name}"
                            authors.append(full_name)
                    
                    # سال انتشار
                    pub_year = "نامشخص"
                    year_elem = article.find('.//PubDate/Year')
                    if year_elem is not None and year_elem.text:
                        pub_year = year_elem.text
                    else:
                        # روش جایگزین برای تاریخ
                        medline_date = article.find('.//PubDate/MedlineDate')
                        if medline_date is not None and medline_date.text:
                            pub_year = medline_date.text[:4]
                    
                    # مجله
                    journal_elem = article.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else "نامشخص"
                    
                    # DOI
                    doi = "نامشخص"
                    doi_elems = article.findall('.//ArticleId')
                    for elem in doi_elems:
                        if elem.get('IdType') == 'doi' and elem.text:
                            doi = elem.text
                            break
                    
                    articles.append({
                        'title': title,
                        'abstract': abstract,
                        'authors': authors[:3],  # ۳ نویسنده اول
                        'year': pub_year,
                        'journal': journal,
                        'doi': doi,
                        'source': 'PubMed',
                        'word_count': len(abstract.split())
                    })
                    
                except Exception as e:
                    print(f"⚠️ خطا در پردازش یک مقاله: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"❌ خطا در پردازش XML: {e}")
            return None

    # بقیه متدها مانند قبل می‌مانند...
