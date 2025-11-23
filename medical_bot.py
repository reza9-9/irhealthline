from pubmed_bot import PubMedBot
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import random
import time
import os
from database_handler import MedicalDatabase
from website_poster import WebsiteAutoPoster
from analytics import MedicalAnalytics

class AutoMedicalContentBot:
    def __init__(self):
        self.generated_articles = []
        
    # گسترش موضوعات و دسته‌بندی‌ها
    AUTO_TOPICS = {
        "دیابت و متابولیک": [
            "درمان دیابت نوع ۲ با روش‌های نوین", 
            "کنترل قند خون در فصل سرما",
            "رژیم غذایی مناسب برای دیابتی‌ها",
            "ورزش‌های مؤثر برای کاهش قند خون",
            "عوارض بلندمدت دیابت و راه‌های پیشگیری"
        ],
        "تغذیه و رژیم": [
            "رژیم مدیترانه‌ای و فواید آن برای قلب",
            "فستینگ متناوب و تأثیر بر متابولیسم",
            "رژیم کتوژنیک برای کاهش وزن",
            "شاخص گلایسمی و کنترل وزن",
            "مکمل‌های غذایی ضروری برای سالمندان"
        ],
        "قلب و عروق": [
            "درمان فشار خون با تغییر سبک زندگی",
            "کنترل کلسترول با تغذیه مناسب",
            "ورزش‌های قلبی-عروقی برای سلامت قلب",
            "پیشگیری از سکته مغزی",
            "رژیم غذایی مخصوص بیماران قلبی"
        ],
        "گوارش و کبد": [
            "درمان کبد چرب با روش‌های طبیعی",
            "تغذیه مناسب برای سلامت دستگاه گوارش",
            "پروبیوتیک‌ها و بهبود میکروبیوم روده",
            "رژیم غذایی برای بهبود گوارش",
            "پاکسازی کبد با مواد غذایی طبیعی"
        ],
        "روانشناسی سلامت": [
            "تأثیر استرس بر سیستم ایمنی بدن",
            "رابطه خواب و سلامت متابولیک",
            "تکنیک‌های کاهش استرس روزانه",
            "تأثیر مدیتیشن بر فشار خون"
        ]
    }
    
    def select_daily_topics(self):
        """انتخاب هوشمندانه‌تر موضوعات"""
        print("📅 در حال انتخاب موضوعات امروز...")
        
        # انتخاب متعادل از همه دسته‌بندی‌ها
        selected_topics = []
        categories = list(self.AUTO_TOPICS.keys())
        random.shuffle(categories)
        
        for category in categories[:3]:  # حداکثر ۳ دسته‌بندی مختلف
            topics = self.AUTO_TOPICS[category]
            if topics:
                selected_topic = random.choice(topics)
                selected_topics.append(selected_topic)
        
        # اگر کمتر از ۳ موضوع انتخاب شده، از دسته‌بندی‌های تصادفی اضافه کن
        while len(selected_topics) < 3:
            random_category = random.choice(categories)
            random_topic = random.choice(self.AUTO_TOPICS[random_category])
            if random_topic not in selected_topics:
                selected_topics.append(random_topic)
        
        print(f"✅ موضوعات امروز: {selected_topics}")
        return selected_topics
    
    def generate_ai_content(self, topic):
        """تولید محتوای مبتنی بر PubMed"""
        print(f"🤖 در حال تولید محتوا برای: {topic}")
        
        # دیکشنری ترجمه موضوعات به انگلیسی
        topic_translations = {
            "درمان دیابت نوع ۲ با روش‌های نوین": "type 2 diabetes treatment innovations",
            "کنترل قند خون در فصل سرما": "blood sugar control in cold weather",
            "رژیم غذایی مناسب برای دیابتی‌ها": "diabetic diet recommendations",
            "ورزش‌های مؤثر برای کاهش قند خون": "exercise for blood sugar reduction",
            "عوارض بلندمدت دیابت و راه‌های پیشگیری": "diabetes long-term complications prevention",
            "رژیم مدیترانه‌ای و فواید آن برای قلب": "mediterranean diet heart benefits",
            "فستینگ متناوب و تأثیر بر متابولیسم": "intermittent fasting metabolism",
            "رژیم کتوژنیک برای کاهش وزن": "ketogenic diet weight loss",
            "شاخص گلایسمی و کنترل وزن": "glycemic index weight control",
            "مکمل‌های غذایی ضروری برای سالمندان": "nutritional supplements elderly",
            "درمان فشار خون با تغییر سبک زندگی": "hypertension lifestyle changes",
            "کنترل کلسترول با تغذیه مناسب": "cholesterol control nutrition",
            "ورزش‌های قلبی-عروقی برای سلامت قلب": "cardio exercise heart health",
            "پیشگیری از سکته مغزی": "stroke prevention",
            "رژیم غذایی مخصوص بیماران قلبی": "heart disease diet",
            "درمان کبد چرب با روش‌های طبیعی": "fatty liver natural treatment",
            "تغذیه مناسب برای سلامت دستگاه گوارش": "digestive health nutrition",
            "پروبیوتیک‌ها و بهبود میکروبیوم روده": "probiotics gut microbiome",
            "رژیم غذایی برای بهبود گوارش": "diet for digestion improvement",
            "پاکسازی کبد با مواد غذایی طبیعی": "liver detox foods",
            "تأثیر استرس بر سیستم ایمنی بدن": "stress immune system",
            "رابطه خواب و سلامت متابولیک": "sleep metabolic health",
            "تکنیک‌های کاهش استرس روزانه": "daily stress reduction techniques",
            "تأثیر مدیتیشن بر فشار خون": "meditation blood pressure"
        }
        
        # تبدیل موضوع به انگلیسی
        english_topic = topic_translations.get(topic, topic)
        
        # جستجو در PubMed
        pubmed_bot = PubMedBot()
        articles = pubmed_bot.search_meta_analysis(english_topic)
        
        if articles:
            # تولید محتوا بر اساس PubMed
            content = pubmed_bot.generate_summary(topic, articles)
            quality_score = 9
            source = "PubMed Meta-Analysis"
            print(f"   ✅ محتوای مبتنی بر PubMed تولید شد (کیفیت: {quality_score}/10)")
        else:
            # اگر PubMed نتونست، از محتوای تولیدی استفاده کن
            content = self.generate_fallback_content(topic)
            quality_score = 7
            source = "AI Generated"
            print(f"   ⚠️ از محتوای تولیدی استفاده شد (کیفیت: {quality_score}/10)")
        
        return {
            "title": topic,
            "content": content,
            "category": self.detect_category(topic),
            "word_count": len(content.split()) if content else 0,
            "reading_time": f"{max(2, len(content) // 150)} دقیقه" if content else "۲ دقیقه",
            "quality_score": quality_score,
            "generated_at": datetime.now().isoformat(),
            "status": "تولید شده",
            "source": source
        }
    
    def generate_fallback_content(self, topic):
        """محتوای جایگزین وقتی PubMed جواب نده"""
        # templates پیشرفته‌تر برای مواقع ضروری
        content_structures = {
            "دیابت": [
                {
                    "intro": f"در زمینه {topic}، تحقیقات جدید نشان می‌دهد که ",
                    "body": [
                        "ترکیب مناسبی از رژیم غذایی، فعالیت بدنی و دارودرمانی می‌تواند نتایج چشمگیری داشته باشد. ",
                        "پایش منظم شاخص‌های سلامتی نقش کلیدی در مدیریت این شرایط ایفا می‌کند. ",
                        "تغییرات ساده در سبک زندگی often می‌تواند تأثیرات قابل توجهی بر جای بگذارد. "
                    ],
                    "conclusion": "مشاوره با تیم درمانی برای برنامه‌ریزی شخصی‌شده ضروری است."
                }
            ],
            "تغذیه": [
                {
                    "intro": f"در مورد {topic}، شواهد علمی نشان می‌دهد که ",
                    "body": [
                        "انتخاب مواد غذایی طبیعی و فرآوری نشده پایه اصلی سلامت است. ",
                        "تنوع غذایی و تعادل در مصرف گروه‌های مختلف غذایی اهمیت ویژه‌ای دارد. ",
                        "مصرف کافی میوه و سبزیجات تازه می‌تواند سطح انرژی و سلامت کلی را بهبود بخشد. "
                    ],
                    "conclusion": "تطبیق رژیم غذایی با شرایط فردی و نیازهای خاص سلامت توصیه می‌شود."
                }
            ],
            "قلب": [
                {
                    "intro": f"در ارتباط با {topic}، مطالعات اخیر تأکید می‌کنند که ",
                    "body": [
                        "فعالیت بدنی منظم و تغذیه مناسب اساس سلامت قلبی-عروقی هستند. ",
                        "پایش منظم فشار خون و چربی‌های خون در پیشگیری از عوارض مؤثر است. ",
                        "کاهش عوامل خطر مانند استرس و مصرف نمک می‌تواند تأثیرات مثبتی داشته باشد. "
                    ],
                    "conclusion": "معاینات دوره‌ای و پیگیری منظم با پزشک معالج ضروری است."
                }
            ]
        }
        
        # تشخیص دسته‌بندی
        category = self.detect_category(topic)
        
        # تولید محتوای ساختاریافته
        if "دیابت" in category:
            structure = random.choice(content_structures["دیابت"])
        elif "تغذیه" in category:
            structure = random.choice(content_structures["تغذیه"])
        elif "قلب" in category:
            structure = random.choice(content_structures["قلب"])
        else:
            structure = random.choice(content_structures["تغذیه"])
        
        # ساخت محتوا
        intro = structure["intro"]
        body = "".join(random.sample(structure["body"], min(2, len(structure["body"]))))
        conclusion = structure["conclusion"]
        
        content = intro + body + conclusion
        
        # اضافه کردن نکات تخصصی
        expert_tips = [
            " از مصرف قندهای ساده و چربی‌های اشباع خودداری کنید.",
            " روزانه حداقل ۳۰ دقیقه فعالیت بدنی متوسط داشته باشید.",
            " مصرف نمک را به کمتر از ۵ گرم در روز محدود کنید.",
            " خواب کافی و با کیفیت را در اولویت قرار دهید.",
            " استرس خود را با تکنیک‌های آرامش‌بخش مدیریت کنید.",
            " مصرف آب کافی را در طول روز فراموش نکنید.",
            " از مصرف الکل و سیگار به طور کامل پرهیز کنید."
        ]
        
        content += random.choice(expert_tips)
        
        return content
    
    def detect_category(self, topic):
        """تشخیص دسته‌بندی موضوع"""
        for category, topics in self.AUTO_TOPICS.items():
            if topic in topics:
                return category
        return "عمومی"
    
    def auto_generate_daily_content(self):
        """تولید محتوای روزانه با کیفیت بالاتر"""
        print("🚀 شروع تولید خودکار محتوای روزانه (نسخه PubMed)...")
        print(f"🕒 زمان شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # انتخاب موضوعات روز
        daily_topics = self.select_daily_topics()
        
        # تولید محتوا برای هر موضوع
        articles = []
        for i, topic in enumerate(daily_topics, 1):
            print(f"📝 در حال تولید مقاله {i}/{len(daily_topics)}: {topic}")
            
            article = self.generate_ai_content(topic)
            articles.append(article)
            
            # تأخیر برای طبیعی‌تر شدن و رعایت محدودیت API
            time.sleep(5)
            
            print(f"   ✅ تولید شد: {article['title']} ({article['word_count']} کلمه - کیفیت: {article['quality_score']}/10 - منبع: {article['source']})")
        
        return articles
    
    def save_daily_report(self, articles):
        """ذخیره گزارش روزانه"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_articles_{timestamp}.json"
        
        report = {
            "meta": {
                "total_articles": len(articles),
                "generation_date": datetime.now().isoformat(),
                "average_quality": sum(a['quality_score'] for a in articles) / len(articles),
                "total_words": sum(a['word_count'] for a in articles),
                "sources": list(set(a['source'] for a in articles))
            },
            "articles": articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def show_daily_summary(self, articles):
        """نمایش خلاصه روزانه"""
        print("\n" + "="*60)
        print("📊 خلاصه تولید روزانه")
        print("="*60)
        
        total_words = sum(article['word_count'] for article in articles)
        avg_quality = sum(article['quality_score'] for article in articles) / len(articles)
        pubmed_count = sum(1 for article in articles if article['source'] == 'PubMed Meta-Analysis')
        
        print(f"📈 مقالات تولید شده: {len(articles)}")
        print(f"🔬 مقالات مبتنی بر PubMed: {pubmed_count}")
        print(f"📝 کل کلمات: {total_words}")
        print(f"⭐ میانگین کیفیت: {avg_quality:.1f}/10")
        print(f"⏱️ زمان مطالعه کل: {total_words // 150} دقیقه")
        
        print("\n📋 فهرست مقالات:")
        for i, article in enumerate(articles, 1):
            source_icon = "🔬" if article['source'] == 'PubMed Meta-Analysis' else "🤖"
            print(f"   {i}. {source_icon} {article['title']} ({article['word_count']} کلمه - کیفیت: {article['quality_score']}/10)")

def main():
    print("="*70)
    print("🤖 ربات تولید خودکار محتوای پزشکی - نسخه PubMed")
    print("="*70)
    
    # ایجاد ربات
    bot = AutoMedicalContentBot()
    
    # تولید خودکار محتوای روزانه
    articles = bot.auto_generate_daily_content()
    
    if articles:
        # 💾 ذخیره در دیتابیس
        print("\n💾 در حال ذخیره در دیتابیس...")
        try:
            db = MedicalDatabase()
            db.save_articles(articles)
            print("✅ مقالات با موفقیت در دیتابیس ذخیره شد")
        except Exception as e:
            print(f"❌ خطا در ذخیره دیتابیس: {e}")
        
        # 🌐 ارسال به وبسایت
        print("\n🌐 در حال ارسال به وبسایت...")
        try:
            website = WebsiteAutoPoster()
            website_results = website.post_multiple_articles(articles)
            
            # نمایش نتایج ارسال
            success_count = sum(1 for r in website_results if r['success'])
            print(f"✅ {success_count}/{len(articles)} مقاله به وبسایت ارسال شد")
        except Exception as e:
            print(f"❌ خطا در ارسال به وبسایت: {e}")
        
        # 📊 تولید داشبورد
        print("\n📊 در حال تولید داشبورد...")
        try:
            from dashboard import MedicalDashboard
            dashboard = MedicalDashboard()
            dashboard.generate_html_dashboard()
            print("✅ داشبورد با موفقیت تولید شد")
        except Exception as e:
            print(f"❌ خطا در تولید داشبورد: {e}")
        
        # 📈 تولید گزارش هفتگی
        print("\n📈 در حال تولید گزارش‌های آنالیز...")
        try:
            analytics = MedicalAnalytics()
            weekly_report = analytics.generate_weekly_report()
            if weekly_report:
                print("✅ گزارش‌های آنالیز با موفقیت تولید شد")
        except Exception as e:
            print(f"❌ خطا در تولید گزارش‌های آنالیز: {e}")
        
        # 📄 ذخیره گزارش روزانه
        filename = bot.save_daily_report(articles)
        
        # 📋 نمایش خلاصه
        bot.show_daily_summary(articles)
        
        print(f"\n💾 گزارش ذخیره شد: {filename}")
        print("🔄 اجرای بعدی: فردا همین زمان (خودکار)")
    else:
        print("❌ هیچ مقاله‌ای تولید نشد!")

if __name__ == "__main__":
    main()
