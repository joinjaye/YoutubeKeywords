# 最后的合并

import pandas as pd

targets = ["Bitget", "Bingx", "Zoomex", "Mexc"]
final  = pd.DataFrame()

for target in targets:
    df = pd.read_csv(f"{target}_final.csv")
    final = pd.concat([final, df], ignore_index=True)

keyword_final = final.groupby("Keyword").agg({"Views": "sum", "lang": "first", "Top 3 Pages": "first", "Class": lambda x: ", ".join(x.astype(str))}).sort_values(by="Views", ascending=False).reset_index()
print(keyword_final)

final.to_csv("final.csv")
keyword_final.to_csv("keyword_final.csv")

