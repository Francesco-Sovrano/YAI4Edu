from bs4 import BeautifulSoup
import re
import sys

file = sys.argv[1]

with open(file) as f: 
	xml = f.read()

y=BeautifulSoup(xml, features="lxml")
get_text = lambda x: re.sub(r'[ \n\t]+',' ',x.text)

for p in y.findAll("p"):
	print(get_text(p))
	print('parents',[(a.name, a.attrs) for a in p.find_parents()])
	for ref in p.findAll('ref', recursive=False):
		print('Reference:', get_text(ref), ref['href'])
	blockList = p.find_parent('blocklist')
	if blockList:
		print('Block List:', blockList['eid'])
		listIntroduction = blockList.listintroduction
		print('List Introduction:', get_text(listIntroduction))
		item = p.find_parent('item')
		print('Item:', item['eid'], get_text(item.num))
		exit
	paragraph = p.find_parent('paragraph')
	if paragraph:
		article = paragraph.find_parent('article')
		print('Article:', article['eid'], get_text(article.num))
		print('Paragraph:', paragraph['eid'], get_text(paragraph.num) if paragraph.num else None)
	print('#'*100)