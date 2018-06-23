from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os
from urllib.request import urlopen
import shutil
import argparse
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from utils import page_parser

PLACEHOLDER = 'broken_page.jpg'
IMG_EXT = '.jpg'
BLOCK_SZ = int(2**13)
WIDGETS = ['Progress: ',
           Percentage(),
           ' ', Bar(marker=RotatingMarker(), left='[', right=']'),
           ' ', ETA()]


def parse_args():
    """Parse input argument
    """
    # parse input argument
    parser = argparse.ArgumentParser(
        description='Download comic from readcomiconline.to')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--chapurl', type=str,
                       help='The url of a comic chapter')
    group.add_argument('-l', '--chaplst', type=str,
                       help='File contains list of comic\'s chapter url')
    group.add_argument('-s', '--serurl', type=str,
                       help='The url of a whole comic series')
    parser.add_argument('-d', '--dest', type=str, default='comics',
                        help='Destination to store comic')
    args = parser.parse_args()

    # make destination folder
    if not os.path.exists(args.dest):
        os.mkdir(args.dest)
    return args


def dir_2_cbz(dir_pth):
    """Convert a directory to cbz format.

    Original directory is deleted after converging

    Args:
        dir_pth: path to the directory
    """
    shutil.make_archive(dir_pth, 'zip', dir_pth)
    shutil.rmtree(dir_pth)
    os.rename(dir_pth+'.zip', dir_pth+'.cbz')
    pass


def download_data(url, filename, dst_dir):
    """Download data from a given url

    Args:
        url: url of the data
        filename: name for the file to store the data
        dst_dir: where the file is saved
    """
    fullpath = os.path.join(dst_dir, filename)
    if os.path.exists(fullpath):
        return

    # Try to open url
    try:
        page = urlopen(url)
    except Exception:
        shutil.copy(PLACEHOLDER, fullpath)
        return

    f = open(fullpath, 'wb')
    while True:
        buff = page.read(BLOCK_SZ)
        if not buff:
            break
        f.write(buff)
    f.close()
    pass


def download_chapter(chap_url, dest, chap_name=None, compress=True):
    """Download a chapter of comic

    Args:
        chap_url: url of the chapter
        dest: where the chapter is saved
        chap_name: specify the name of the chapter. If None (default) then
            the chapter name is generated from chapter's url
        compress: whether to convert the chapter to cbz file, True by default
    """
    # parse name from chapter's url
    tokens = chap_url.split('/')
    comic_name = tokens[-2]
    if chap_name is None:
        chap_name = tokens[-1].split('?')[0]

    # get url list of all pages
    pg_url_lst = page_parser.get_page_url_list(chap_url)
    assert len(pg_url_lst) > 0, 'No pages found!'

    # set up environment
    comic_pth = os.path.join(dest, comic_name)
    if not os.path.exists(comic_pth):
        os.mkdir(comic_pth)
    chap_pth = os.path.join(comic_pth, chap_name)
    if not os.path.exists(chap_pth):
        os.mkdir(chap_pth)

    # download each page
    page = 0
    # pbar = ProgressBar(widgets=WIDGETS, maxval=len(pg_url_lst)).start()
    pbar = ProgressBar(maxval=len(pg_url_lst))
    for url in pg_url_lst:
        page += 1
        page_name = 'pg_{:03d}{}'.format(page, IMG_EXT)
        download_data(url, page_name, chap_pth)
        pbar.update(page)
    pbar.finish()

    # compress and convert to cbz
    if compress:
        dir_2_cbz(os.path.join(comic_pth, chap_name))
    pass


def main():
    # Parse input argguments
    args = parse_args()

    # download comic depending on the input method
    sep = '_'*80

    # Download by chapter
    if args.chapurl is not None:
        download_chapter(args.chapurl, args.dest)
    # Download by a list of chapter
    elif args.chaplst is not None:
        assert os.path.exists(args.chaplst), \
            'File does not exist {}'.format(args.chaplst)
        with open(args.chaplst, 'r') as f:
            chap_url_list = f.read().splitlines()

        for chap_url in chap_url_list:
            print('{}\n{}'.format(sep, chap_url))
            download_chapter(chap_url, args.dest)
            print('\n')
    # Download by series
    elif args.serurl is not None:
        # request starting and stopping indices
        start = input(
            'Starting chapter index (Enter for the first chapter): ')
        stop = input('Ending chapter index (Enter for the last chapter): ')

        # convert start and stop to int
        start = int(start) if start != '' else None
        stop = int(stop) if stop != '' else None

        # parse names and slice content
        comic_name = args.serurl.split('/')[-1]
        print('Comic:', comic_name)
        chap_url_lst, chap_name_lst = page_parser.get_chapter_url_list(
            args.serurl)
        chap_url_lst = chap_url_lst[start:stop]
        chap_name_lst = chap_name_lst[start:stop]
        num_chaps = len(chap_url_lst)
        print(num_chaps, 'chapters found')

        # download selected chapters in the series
        for i in range(num_chaps):
            print('{}\n{}'.format(sep, chap_url_lst[i]))
            download_chapter(
                chap_url_lst[i], args.dest, chap_name=chap_name_lst[i])
            print('\n')
    pass


if __name__ == '__main__':
    main()
