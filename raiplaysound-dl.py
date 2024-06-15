#!/usr/bin/env python3
# Download the audios from raiplay audiobooks.
# Catalog: https://www.raiplaysound.it/programmi/adaltavoce/audiolibri
# Usage example:
#   ./download_raiplaysound.py https://www.raiplaysound.it/audiolibri/latortaincielo
import requests
import re
from urllib.parse import urljoin
import sys

filename_template="{number:02d}. {title}.mp3"

def download_file(session, url, filename):
    with session.get(url, stream=True) as response:
        response.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    file.write(chunk)

def main(audiobook_url):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:126.0) Gecko/20100101 Firefox/126.0"
    })

    html = session.get(audiobook_url).text

    json_index_relative_url = re.search('parent_path_id="([^"]*)"', html).groups()[0]
    json_index_absolute_url = urljoin(audiobook_url, json_index_relative_url)
    json_index_content = session.get(json_index_absolute_url).json()

    for (i, card) in enumerate(json_index_content['block']['cards'], start=1):
        url = card.get('downloadable_audio', card['audio'])['url']
        filename = filename_template.format(
            number=i,
            title=re.sub('[^A-z0-9. ]', '-', card['title'])
        )
        print(f"Downloading {filename}…")
        download_file(session, url, filename)

if __name__ == '__main__':
    main(sys.argv[1])
