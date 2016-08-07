import os, sys
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
	""" Retrieve the list of page url from a chapter
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
	print 'Downloading %s Bytes: %s' %(filename, filesize)
	
	pbar = ProgressBar(widgets=WIDGETS, maxval=filesize).start()
	filesize_dl = 0
	while True:
		buff = page.read(BLOCK_SZ)
		if not buff:
			break
		f.write(buff)
		filesize_dl += len(buff)
		pbar.update(filesize_dl)
	pbar.finish()
	f.close()
	return


def download_chapter(chap_url, dest, compress=True):
	""" Download a chapter of comic
		Input:
			chap_url: url of the chapter
			dest: where the chapter is saved
			compress: whether to convert the chapter to cbz file, True by default
		Output:
			None
	"""
	# parse name from chapter's url
	tokens = chap_url.split('/')
	comic_name = tokens[-2]
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
	for url in pg_url_lst:
		page += 1
		page_name = 'pg_'+str(page).zfill(3)+IMG_EXT
		download_data(url, page_name, chap_pth)

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
	if argv.chapurl is not None:
		download_chapter(argv.chapurl, argv.dest)
	elif argv.serurl is not None:
		comic_name = argv.chapurl.split('/')[-1]
		print 'Not implemented yet'
		exit()
	elif argv.file is not None:
		with open(argv.file,'r') as f:
			chap_url_list = f.read().splitlines()
		for chap_url in chap_url_list:
			print '=========================================================='
			print chap_url
			print '=========================================================='
			download_chapter(chap_url, argv.dest)
			print '\n\n'