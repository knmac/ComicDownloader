import cfscrape, ipdb

INVALID_CHAR = '\/:*?"<>|'

def get_page_url_list(chap_url):
	""" Retrieve the list of page url from give chapter's url
		Input:
			chap_url: url of the chapter
		Output:
			pg_url_lst: list of page url
	"""
	print 'Getting content from chapter\'s url...'
	scraper = cfscrape.create_scraper()
	page = scraper.get(chap_url)
	page = page.content.splitlines()

	pg_url_lst = []
	for line in page:
		if 'lstImages.push' in line:
			url = line.lstrip()
			url = url.replace('lstImages.push("', '')
			url = url.replace('");', '')
			pg_url_lst.append(url)
	return pg_url_lst


def get_chapter_url_list(series_url):
	""" Retrieve the list of chapter url from given series' url
		Input:
			series_url: url of the series
		Output:
			chap_url_lst: list of chapter url
			chap_name_lst: list of chapter name
	"""
	print 'Getting content from series\' url...'
	scraper = cfscrape.create_scraper()
	page = scraper.get(series_url)
	lines = page.content.splitlines()

	# find the table containing chapters' url
	for pos in range(len(lines)):
		if '<table class="listing">' in lines[pos]:
			break

	# parse chapters' url
	chap_url_lst, chap_name_lst = [], []
	while not '</table>' in lines[pos]:
		if 'href' in lines[pos]:
			# parse url
			raw_url = lines[pos].lstrip()
			raw_url = raw_url.split('"')[1]
			url = series_url + '/' + raw_url.split('/')[-1]
			chap_url_lst.append(url)

			# parse name
			name = lines[pos+2].lstrip()
			name = name.replace('</a>','')
			for c in INVALID_CHAR:
				name = name.replace(c, '')
			chap_name_lst.append(name)
			pos += 2
		pos += 1

	# reverse the list (because latest chapter is on top by default)
	chap_name_lst.reverse()
	chap_url_lst.reverse()
	return chap_url_lst, chap_name_lst
