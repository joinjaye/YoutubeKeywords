# youtube_keywords.py里爬取tag之后，最后对处理数据并输出csv的部分存在bug懒得改了orz。用这个文件进行数据处理。

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import langid

keyword = "Bingx"
df = pd.read_csv(f"{keyword}_tags.csv")

def language_dection(text):
    try:
        lang, _ = langid.classify(text)
        if lang == "en":
            return "en"
        else:
            return lang
    except:
        return "unknown"
    
def video_language():
    df["lang"] = df["Intro"].apply(language_dection)
    return df

def keyword_agg():

    def view_num(x):
        x = x[:-3]
        if "万" in x:
            return float(x[:-1]) * 10000
        try:
            return int(x)
        except:
            return 0
        
    df = video_language()
    df["views"] = df["Views"].apply(view_num)
    keywords = {}
    for index, row in df.iterrows():
        try:
            hashlist = set(row["Hashtags"][2:-2].split("', '"))
            for hash in hashlist:
                if hash in keywords:
                    keywords[hash] += row["views"]
                else:
                    keywords[hash] = row["views"]
        except:
            pass
    
    keywords = {k: v for k, v in sorted(keywords.items(), key=lambda item: item[1], reverse=True)}
    if "t Fou" in keywords:
        del keywords["t Fou"]
    if "" in keywords:
        del keywords[""]
    
    keyworddf = pd.DataFrame(keywords.items(), columns=["Keyword", "Views"])
    keyworddf["lang"] = keyworddf["Keyword"].apply(language_dection)
    
    def match_the_most_viewed_3_pages_for_each_keyword(item):
        pages = df[df["Hashtags"].str.contains(item, na=False)]
        pages = pages.sort_values(by="views", ascending=False)
        return "\n".join([f"{i}: {j}" for i, j in zip(pages.head(3)["views"], pages.head(3)["Link"])])
        
    keyworddf["Top 3 Pages"] = keyworddf["Keyword"].apply(match_the_most_viewed_3_pages_for_each_keyword)
    keyworddf["Class"] = keyword
    keyworddf.to_csv(f"{keyword}_final.csv", index=False)

keyword_agg()