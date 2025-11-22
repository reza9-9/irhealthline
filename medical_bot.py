def main():
    print("🚀 ربات تولید محتوای پزشکی فعال شد!")
    
    bot = MedicalContentBot()
    
    # ۱. جستجو
    keywords = ["diabetes", "cancer", "cardiology"]
    articles = bot.search_medical_sources(keywords)
    
    # ۲. ترجمه
    for article in articles:
        article['title_fa'] = bot.translate_content(article['title'])
        article['summary_fa'] = bot.translate_content(article['summary'])
    
    # ۳. نمایش نتایج
    print("\n📊 مقالات تولید شده:")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title_fa']}")
        print(f"   📝 {article['summary_fa']}")
        print(f"   🏷️ {article['category']}")
        print()
    
    # ۴. ذخیره
    output_file = bot.save_to_json(articles)
    
    print(f"✅ پردازش کامل شد!")
    print(f"📁 فایل خروجی: {output_file}")

if __name__ == "__main__":
    main()
