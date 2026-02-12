import feedparser
import urllib.parse

def clean_company_name(full_name):
    """
    [名稱清洗]
    移除贅字，提高搜尋命中率
    """
    name = full_name.replace("股份有限公司", "").replace("有限公司", "")
    name = name.replace("（股）公司", "").replace("(股)公司", "")
    name = name.replace("-KY", "").replace("*", "")
    return name.strip()

def search_news(company_name, news_type='negative'):
    """
    [新聞搜尋 V8.0 - 雙向雷達版]
    news_type='positive': 搜利多 (營收、獲利、得獎)
    news_type='negative': 搜利空 (弊案、意外、裁罰)
    """
    if not company_name: return []

    target_name = clean_company_name(company_name)
    
    if news_type == 'positive':
        # === 設定正面關鍵字 ===
        keywords = [
            "營收新高", "獲利創新高", "成長", "表揚", 
            "得獎", "配息", "殖利率", "優良", "訂單", "擴廠"
        ]
        # 排除負面詞 (避免搜到 "獲利衰退" 或 "工安意外賠償")
        exclude_terms = ["衰退", "虧損", "弊案", "意外", "裁罰", "重挫"]
        print(f"🕵️‍♀️ 正在挖掘 {target_name} 的【好消息】...")
        
    else:
        # === 設定負面關鍵字 ===
        keywords = [
            "弊案", "掏空", "工安意外", "判刑", "起訴", 
            "違約", "假帳", "裁罰", "停工", "汙染", 
            "求償", "爭議", "重罰", "違規"
        ]
        # 排除正面詞 (避免搜到 "工安優良獎")
        exclude_terms = ["表揚", "獲獎", "新高", "成長", "優良", "金質獎"]
        print(f"🕵️‍♀️ 正在掃描 {target_name} 的【壞消息】...")

    # 組合查詢
    keywords_or = " OR ".join(keywords)
    query = f'"{target_name}" ({keywords_or})'
    encoded_query = urllib.parse.quote(query)
    
    # Google News RSS
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    results = []
    
    try:
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            date_pub = entry.published if 'published' in entry else ''
            
            # --- 嚴格過濾邏輯 ---
            
            # 1. 標題必須包含公司名稱
            if target_name not in title:
                continue
            
            # 2. 排除不該出現的詞
            is_excluded = False
            for bad_word in exclude_terms:
                if bad_word in title:
                    is_excluded = True
                    break
            
            if is_excluded:
                continue

            # 3. 加入結果
            results.append({
                "標題": title,
                "連結": link,
                "日期": date_pub,
                "來源": entry.source.title if 'source' in entry else 'Google News'
            })
            
            # 兩邊各取前 5 則就好，版面比較好看
            if len(results) >= 5:
                break

    except Exception as e:
        print(f"   ❌ 搜尋錯誤: {e}")
        return []

    return results