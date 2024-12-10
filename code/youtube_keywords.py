#爬取tag之后，最后对处理数据并输出csv的部分存在bug。用temp.py进行数据处理。

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import langid

class Youtube():
    def __init__(self, keyword):
        self.chrome_options = Options()
        self.service = Service(ChromeDriverManager().install())
    
        self.chrome_options.add_argument("--no-sandbox")  # 解决权限问题
        self.chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存不足问题
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36"
        self.chrome_options.add_argument(f"user-agent={user_agent}")
        
        self.keyword = keyword

    def get_links(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://www.youtube.com/")
        search_box = self.driver.find_element("name", "search_query")
        search_box.send_keys(self.keyword)
        search_box.submit()
        time.sleep(5)

        scroll_pause_time = 2  # 每次滚动后的等待时间
        scroll_count = 50
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")

        for _ in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        links = []
        titles = []
        views = []
        videos = self.driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
        for video in videos:
            title = video.find_element(By.ID, "video-title").text
            link = video.find_element(By.ID, "video-title").get_attribute("href")
            view = video.find_element(By.CSS_SELECTOR, "span.style-scope.ytd-video-meta-block").text
            titles.append(title)
            links.append(link)
            views.append(view)
            print(f"Title: {title}\nLink: {link}\nViews: {view}\n")
        
        self.driver.quit()

        df = pd.DataFrame({"Title": titles, "Link": links, "Views": views})
        df.to_csv(f"{self.keyword}_links.csv", index=False)

        return df

    def get_keywords(self):
        df = self.get_links()
        intros = []
        hashtags = []

        for link in df["Link"]:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get(link)
            time.sleep(1)
            try:
                detail_button = self.driver.find_element(By.ID, "expand")
                detail_button.click()
                intro = self.driver.find_element(By.ID, "description-inline-expander").text
                intros.append(intro)
                hashtags.append(re.findall(r"#(\w+)", intro))
            except:
                intros.append("")
                hashtags.append("")

            self.driver.quit()
        
        df["Intro"] = intros
        df["Hashtags"] = hashtags
        return df
    
    def language_dection(self, text):
        try:
            lang, _ = langid.classify(text)
            if lang == "en":
                return "en"
            else:
                return lang
        except:
            return "unknown"
        
    def video_language(self):
        df = self.get_keywords()
        df["lang"] = df["Intro"].apply(self.language_dection)
        df.to_csv(f"{self.keyword}_tags.csv", index=False)
        return df
    
    def view_num(x):
        x = x[:-3]
        if "万" in x:
            return float(x[:-1]) * 10000
        try:
            return int(x)
        except:
            return 0
        
    def match_the_most_viewed_3_pages_for_each_keyword(item, df):
        pages = df[df["Hashtags"].str.contains(item, na=False)]
        pages = pages.sort_values(by="views", ascending=False)
        return "\n".join([f"{i}: {j}" for i, j in zip(pages.head(3)["views"], pages.head(3)["Link"])])
    
    def keyword_agg(self):     

        df = self.video_language()
        df["views"] = df["Views"].apply(self.view_num)

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
        keyworddf["lang"] = keyworddf["Keyword"].apply(self.language_dection)
        
        keyworddf["Top 3 Pages"] = keyworddf["Keyword"].apply(self.match_the_most_viewed_3_pages_for_each_keyword, df=df)
        keyworddf["Class"] = self.keyword
        keyworddf.to_csv(f"{self.keyword}_final.csv", index=False)

targets = ["Bitget", "Bingx", "Zoomex", "Mexc"]

for target in targets:
    youtube = Youtube(target)
    youtube.keyword_agg()
    print(f"{target} Done")
    print("-" * 50)