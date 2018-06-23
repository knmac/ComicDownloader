#!/usr/bin/env bash
# Example of downloading by chapter URL
python downloader.py \
    --chapurl "http://readcomiconline.to/Comic/Batman-Hush/Issue-1?id=21715"

# Example of downloading by list of chapter URLs
python downloader.py \
    --chaplst chap_url.lst

# Example of downloading by series URL
python downloader.py \
    --serurl "http://readcomiconline.to/Comic/Batman-Hush"
