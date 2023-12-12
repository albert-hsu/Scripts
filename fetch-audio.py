# Usage: mkdir ~/Downloads/FOLDER_1;python3 fetch-audio.py <input 2>error >output

import html.parser
import urllib.request
import urllib.parse
import sys
import os.path
import time
from typing_extensions import assert_never

DELAY = 0.25 # seconds
HTTP_TIMEOUT = 30 # seconds

class MyHtmlParser(html.parser.HTMLParser):
    __possible = False
    __found = False

    __target = None
    __results = []

    def search(self, html, target):
        self.__target = target
        self.__results = []
        self.reset()
        self.feed(html)
        return self.__results

    def __value(self, attrs, name):
        for a in attrs:
            if len(a) == 2 and a[0] == name:
                return a[1]
        return None

    def __match(self, value, check):
        if isinstance(value, str):
            return check(value)
        return False

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            if self.__match(self.__value(attrs, "class"), lambda x: x.endswith(" ure")):
                self.__possible = True
        elif tag == "h1":
            if self.__value(attrs, "class") == "hword":
                self.__possible = True
        elif tag == "a":
            if self.__match(self.__value(attrs, "class"), lambda x: x.startswith("play-pron-v2 ")):
                if self.__found:
                    self.__found = False

                    data_dir = None
                    data_file = None

                    val = self.__value(attrs, "data-lang")
                    if val != "en_us":
                        assert_never('"{}" data-lang: "{}"'.format(self.__target, val))

                    val = self.__value(attrs, "data-dir")
                    if val is not None:
                        data_dir = val

                    val = self.__value(attrs, "data-file")
                    if val is not None:
                        data_file = val
                            
                    if data_dir is None or data_file is None:
                        assert_never('"{}" data-dir: "{}" data-file: "{}"'.format(self.__target, data_dir, data_file))

                    self.__results.append("https://HOST_2/audio/prons/en/us/mp3/{}/{}.mp3".format(data_dir, data_file))

    def handle_endtag(self, tag):
        self.__possible = False

    def handle_data(self, data):
        if self.__possible and data == self.__target:
            self.__found = True

    # For `with` statement
    def __enter__(self):
        return self.__class__()

    def __exit__(self, type, value, traceback):
        self.close()

def fetch_html_content(url):
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response:
        return response.read().decode()

def download_file(url, out):
    # Download with urllib.request.urlretrieve(), which has no timeout option, may hang the program.
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as response, open(out, "wb") as f:
        f.write(response.read())

def main():
    outputDirectory = os.path.join(os.path.expanduser("~"), "Downloads/FOLDER_1/")
    if not os.path.isdir(outputDirectory):
        print('E: output directory "{}" does not exist'.format(outputDirectory), file=sys.stderr)
        sys.exit(os.EX_CANTCREAT)

    targets = []
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        targets.append(line)

    result = {}

    with MyHtmlParser() as parser:
        for target in targets:
            time.sleep(DELAY)

            host = "HOST_1"
            # urllib.parse.quote() performs percent-encoding on characters such as space and accented characters.
            path = urllib.parse.quote("/dictionary/{}".format(target))

            try:
                htmlText = fetch_html_content("https://" + host + path)
            except urllib.error.URLError as ex:
                print('"{}" E: {}'.format(target, ex), file=sys.stderr)
                continue
            except urllib.error.HTTPError as ex:
                print('"{}" E: {}'.format(target, ex), file=sys.stderr)
                continue
            except TimeoutError as ex:
                print('"{}" E: {}'.format(target, ex), file=sys.stderr)
                continue

            found = parser.search(htmlText, target)

            assert(type(found) is list)
            if len(found) == 0:
                print('"{}" does not found😰'.format(target), file=sys.stderr)
            else:
                for f in found:
                    basename = os.path.basename(f)
                    out = os.path.join(outputDirectory, basename)
                    
                    try:
                        if not os.path.isfile(out):
                            download_file(f, out)
                        if result.get(target) is None:
                            result[target] = set([basename])
                        else:
                            result[target].add(basename)
                    except TimeoutError as ex:
                        print('"{}" E: {}'.format(target, ex), file=sys.stderr)
                    except Exception as ex:
                        print('"{}" E: {}'.format(target, ex), file=sys.stderr)

        for w in targets:
            if w in result:
                print("{}, {}".format(w, " ".join(list(result[w]))))
            else:
                print(w)

if __name__ == "__main__":
    main()
