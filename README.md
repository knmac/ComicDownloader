# ComicDownloader

## Overview
Allow downloading with a given url of a chapter or a file containing chapter urls
For the time being, support readcomiconline.to


## Usage
For more information about how to use downloader.py, type
```bash
python downloader.py -h
```

(Result)
```bash
usage: downloader.py [-h] (-c CHAPURL | -s SERURL | -f FILE) [-d DEST]

optional arguments:
  -h, --help  show this help message and exit
  -c CHAPURL  The url of a comic chapter
  -s SERURL   The url of a whole comic series
  -f FILE     File contains list of comic's chapter url
  -d DEST     Destination to store comic
```

## Dependencies
- cfscraper
- progressbar

To install depencies, type
```bash
pip install -r requirements.txt
```
