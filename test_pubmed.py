# test_pubmed.py
from pubmed_bot import PubMedBot

def test_pubmed():
    print("🧪 تست PubMedBot در GitHub Actions...")
    print("=" * 50)
    
    bot = PubMedBot()
    
    # تست با موضوع ساده
    topics = ["diabetes", "hypertension", "liver health"]
    
    for topic in topics:
        print(f"\n🔍 جستجوی: {topic}")
        articles = bot.search_meta_analysis(topic)
        
        if articles:
            print(f"✅ {len(articles)} مقاله پیدا شد")
            for i, article in enumerate(articles, 1):
                print(f"   {i}. {article['title'][:60]}...")
        else:
            print("❌ مقاله‌ای پیدا نشد")

if __name__ == "__main__":
    test_pubmed()
