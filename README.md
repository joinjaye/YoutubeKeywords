# YoutubeKeywords
## 属性说明				
				
### byChannelAndKeyword		

各平台在Youtube视频中的关键词数据（在Youtube上搜索对应平台，整合搜索结果中的所有视频数据）	

- Keyword	提取视频介绍部分各hashtag作为关键词			
- Views	该平台在这个关键词上所有相关视频的总浏览量			
- lang	视频介绍部分所用语言			
- Top 3 Pages	该平台在这个关键词上的所有相关视频中，总浏览量最高的三个视频以及相应的浏览量			
- Class	检索输入的平台			
				
### byKeyword				
- 在所搜索的全部平台上，各关键词的整体表现数据				
- Keyword	对byChannelAndKeyword表中按照Keyword列聚合得到			
- Views	带了该关键词的所有视频的总浏览量			
- lang	按照first方式聚合得到			
- Top 3 Pages	按照first方式聚合得到			
- Class	带了该关键词的视频来自的平台

## 注意事项			
			
1. 整合搜索结果中所有视频，未能对不相关视频进行过滤，可能存在垃圾数据（搜索MEXC -> 结果中出现的Mexico相关视频）			
2. 使用时可以通过对lang列进行筛选得到指定语言的关键词相关数据作为参考。但是该列通过python库，对视频intro部分所使用的语言进行分析得到，可能存在不准确的问题。			
