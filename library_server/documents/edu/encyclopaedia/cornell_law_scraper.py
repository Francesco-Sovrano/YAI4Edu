import requests
from bs4 import BeautifulSoup
import os
import tqdm
import time
import sys
import json

from knowpy.misc.jsonld_lib import *


group_keys = ['1','3','4','7','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','Y','Z']

WEBSITE = 'https://www.law.cornell.edu'
FILE_DIR = 'cornell_law'
os.makedirs(FILE_DIR, exist_ok=True)
# Making a GET request

def download_files(file_url_list):
	for file_url in tqdm.tqdm(file_url_list):
		print(f'Downloading {file_url}')
		# if file_url == 'https://www.law.cornell.edu/supct/cert/supreme_court_2014-2015_term_highlights/part_one':
		# 	continue
		file_name = file_url.split('/')[-1]
		file_path = os.path.join(FILE_DIR, file_name+'.json')
		if os.path.exists(file_path):
			continue
		try:
			myfile = requests.get(file_url)
		except Exception as e:
			print(e)
			continue
		soup = BeautifulSoup(myfile.content, 'html.parser')
		related_contents = soup.find('div', {'class': 'field-type-taxonomy-term-reference'})
		content = soup.find('div', {'class': 'field-type-text-with-summary'})
		if not content:
			continue
		file_uri = DOC_PREFIX+get_uri_from_txt(os.path.basename(file_path).replace(' ','_'))
		file_json = {
			'@id': file_uri,
			'my:url': file_url,
			HAS_LABEL_PREDICATE: soup.find('h1', {'id': 'page-title'}).text,
			# 'dbo:abstract': ' '.join([
			# 	p.text.strip() 
			# 	for p in soup.find_all('p') 
			# 	if p.text.strip()
			# ]),
			'my:related_content_list': [
				{
					'@id': WEBSITE+a['href'] if '//' not in a['href'] else a['href'],
					HAS_LABEL_PREDICATE: a.text.strip(),
				}
				for a in related_contents.find_all('a', href=True)
				if a.text.strip()
			] if related_contents else []
		}
		predicate = None
		for t in content.find('div', {'class': 'field-item'}).findChildren():
			if t.name in ['h1','h2','h3']:
				predicate = 'wex:'+t.text.lower().replace(' ','_')
			elif t.name == 'p':
				value = t.text
				if not predicate:
					predicate = 'wex:definition'
				if predicate != 'wex:definition':
					id_ = t.find('a', href=True)
					if id_:
						value = {
							'@id': WEBSITE+id_['href'] if '//' not in id_['href'] else id_['href'],
							HAS_LABEL_PREDICATE: value,
						}
				if predicate in file_json:
					if not isinstance(file_json[predicate], list):
						file_json[predicate] = [file_json[predicate]]
					file_json[predicate].append(value)
				else:
					file_json[predicate] = value
		if isinstance(file_json.get('wex:definition',None), list):
			file_json['wex:definition'] = ' '.join(file_json['wex:definition'])
		# print(json.dumps(file_json, indent=4))
		with open(file_path, 'w') as f:
			json.dump(file_json, f, indent=4)

print('Getting file URLs..')
file_url_list = []
for key in group_keys:
	print(f'from page {key}')
	r = requests.get(f'{WEBSITE}/wex/all/{key}')
	# Parsing the HTML
	soup = BeautifulSoup(r.content, 'html.parser')
	# print(soup.content)

	s = soup.find('div', {"class": "item-list"})
	lines = s.find_all('a', href=True)

	# file_url_list.extend((line.text for line in lines))
	download_files([WEBSITE+line['href'] for line in lines])
	

