import os, sys, ipdb
import urllib2, shutil, argparse
import cfscrape
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA, FileTransferSpeed


IMG_EXT = '.jpg'
BLOCK_SZ = int(2**13)
WIDGETS = ['Progress: ', 
	Percentage(), 
	' ', Bar(marker=RotatingMarker(),left='[',right=']'), 
	' ', ETA(), 
	' ', FileTransferSpeed()]


#====================================================================================
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
			for c in '\/:*?"<>|':
				name = name.replace(c, '')
			chap_name_lst.append(name)
			pos += 2
		pos += 1

	# reverse the list (because latest chapter is on top by default)
	chap_name_lst.reverse()
	chap_url_lst.reverse()
	return chap_url_lst, chap_name_lst


def dir_2_cbz(dir_pth):
	""" Convert a directory to cbz format. Original directory is deleted after converging
		Input:
			dir_pth: path to the directory
	"""
	shutil.make_archive(dir_pth, 'zip', dir_pth)
	shutil.rmtree(dir_pth)
	os.rename(dir_pth+'.zip', dir_pth+'.cbz')
	return


#====================================================================================
def download_data(url, filename, dst_dir):
	""" Download data from a given url
		Input:
			url: url of the data
			filename: name for the file to store the data
			dst_dir: where the file is saved
		Output:
			None
	"""
	fullpath = os.path.join(dst_dir, filename)
	if os.path.exists(fullpath):
		return

	f = open(fullpath, 'wb')
	page = urllib2.urlopen(url)
	meta = page.info()
	filesize = int(meta.getheaders("Content-Length")[0])
	#print 'Downloading %s Bytes: %s' %(filename, filesize)
	
	#pbar = ProgressBar(widgets=WIDGETS, maxval=filesize).start()
	#filesize_dl = 0
	while True:
		buff = page.read(BLOCK_SZ)
		if not buff:
			break
		f.write(buff)
		#filesize_dl += len(buff)
		#pbar.update(filesize_dl)
	#pbar.finish()
	f.close()
	return


def download_chapter(chap_url, dest, chap_name=None, compress=True):
	""" Download a chapter of comic
		Input:
			chap_url: url of the chapter
			dest: where the chapter is saved
			chap_name: specify the name of the chapter. If None (default) then 
				the chapter name is generated from chapter's url
			compress: whether to convert the chapter to cbz file, True by default
		Output:
			None
	"""
	# parse name from chapter's url
	tokens = chap_url.split('/')
	comic_name = tokens[-2]
	if chap_name is None:
		chap_name = tokens[-1].split('?')[0]

	# get url list of all pages
	pg_url_lst = get_page_url_list(chap_url)

	# set up environment
	comic_pth = os.path.join(dest, comic_name)
	if not os.path.exists(comic_pth):
		os.mkdir(comic_pth)
	chap_pth = os.path.join(comic_pth, chap_name)
	if not os.path.exists(chap_pth):
		os.mkdir(chap_pth)

	# download each page
	page = 0
	pbar = ProgressBar(widgets=WIDGETS, maxval=len(pg_url_lst)).start()
	for url in pg_url_lst:
		page += 1
		page_name = 'pg_'+str(page).zfill(3)+IMG_EXT
		download_data(url, page_name, chap_pth)
		pbar.update(page)
	pbar.finish()

	# compress and convert to cbz
	if compress == True:
		dir_2_cbz(os.path.join(comic_pth, chap_name))
	return


#====================================================================================
if __name__ == '__main__':
	# parse input argument
	parser = argparse.ArgumentParser(description='Download comic from readcomiconline.to')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-c', action='store', dest='chapurl', type=str, help='The url of a comic chapter')
	group.add_argument('-s', action='store', dest='serurl', type=str, help='The url of a whole comic series')
	group.add_argument('-f', action='store', dest='file', type=str, help='File contains list of comic\'s chapter url')
	parser.add_argument('-d', action='store', dest='dest', type=str, default='comics', help='Destination to store comic')
	argv = parser.parse_args()

	# make destination folder
	if not os.path.exists(argv.dest):
		os.mkdir(argv.dest)

	# download comic depending on the input method
	sep = '======================================================================='
	if argv.chapurl is not None:
		download_chapter(argv.chapurl, argv.dest)
	elif argv.serurl is not None:
		comic_name = argv.serurl.split('/')[-1]
		chap_url_lst, chap_name_lst = get_chapter_url_list(argv.serurl)
		n = len(chap_url_lst)
		print n,'chapters found'

		for i in range(n):
			print sep + '\n' + chap_url_lst[i] + '\n' + sep
			download_chapter(chap_url_lst[i], argv.dest, chap_name=chap_name_lst[i])
			print '\n\n'
	elif argv.file is not None:
		with open(argv.file,'r') as f:
			chap_url_list = f.read().splitlines()

		for chap_url in chap_url_list:
			print sep + '\n' + chap_url + '\n' + sep
			download_chapter(chap_url, argv.dest)
			print '\n\n'