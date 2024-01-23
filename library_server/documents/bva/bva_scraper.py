import requests
from bs4 import BeautifulSoup
import os
import tqdm
import time
import sys

query = sys.argv[1]

FILE_DIR = f'scraped_files_{query}'
os.makedirs(FILE_DIR, exist_ok=True)
# Making a GET request

def download_files(file_url_list):
	# print('Scraping file URLs..')
	for file_url in tqdm.tqdm(file_url_list):
		file_name = file_url.split('/')[-1]
		file_path = os.path.join(FILE_DIR, file_name)
		if not os.path.exists(file_path):
			myfile = requests.get(file_url)
			open(file_path, 'wb').write(myfile.content)


print('Getting file URLs..')
file_url_list = []
i = 500
year = 9162 # starts from 2021
finding_files = True
while finding_files:
	try:
		print(f'from page {i}')
		r = requests.get(f'https://search.usa.gov/search?affiliate=bvadecisions&dc={year}&query={query}&page={i%500}')
		# r = requests.get(f'https://search.usa.gov/search?affiliate=bvadecisions&query={query}&page={i%500}')
		# Parsing the HTML
		soup = BeautifulSoup(r.content, 'html.parser')
		# print(soup.content)

		s = soup.find('div', {"id": "results"})
		lines = s.find_all('span', {"class": "url"})

		# file_url_list.extend((line.text for line in lines))
		download_files([line.text for line in lines])
		i -= 1
	except Exception as e:
		print(e)
		time.sleep(5)
	if i == 0:
		i = 500
		year -= 1

# print('Scraping file URLs..')
# download_files(file_url_list)
# for file_url in tqdm.tqdm(file_url_list):
# 	file_name = file_url.split('/')[-1]
# 	file_path = os.path.join(FILE_DIR, file_name)
# 	if not os.path.exists(file_path):
# 		myfile = requests.get(file_url)
# 		open(file_path, 'wb').write(myfile.content)
