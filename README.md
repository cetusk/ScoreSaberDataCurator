# ScoreSaberDataCurator
This script `curator.py` fetches an user score data published in the [ScoreSaber](https://scoresaber.com/).

# Preparations

## Python
Install modules for dynamic web scraping ( selenium, beautifulsoup4, html5lib ) and analysis ( Numpy, matplotlib ).
```Bash
python3 -m pip install -r requirements.txt
```

## Chrome
Install the chrome browser for loading a dynamic DOM.
```Bash
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt -y update && \
    apt -y install -y google-chrome-stable
```

Download chrome driver for web scraping using the Selenium.
```Bash
cd /tmp/
wget https://chromedriver.storage.googleapis.com/103.0.5060.53/chromedriver_linux64.zip
apt -y install unzip
```

# Usage

## Set parameters

The 5 of global variables for web scraping and parsing in the `extractor.py`.

|Variable|Context|
|:-|:-|
|`SOURCE_URL`| My page of the [ScoreSaber](https://scoresaber.com/) |
|`WAIT_AJAX_INTERVAL`| Waiting time for loading a dynamic rendering |
|`MAX_PAGE_NUM`| Maximum number of score pages to load |
|`COMMON_HTML_FILENAME`| Output file name header as a HTML; `htmls/COMMON_HTML_FILENAME%d.html`|
|`OUTPUT_LOG_FILENAME`| Output file name as a log file |

For example.
```Python
SOURCE_URL = "https://scoresaber.com/u/76561198993766763"
WAIT_AJAX_INTERVAL = 10.0 # seconds
MAX_PAGE_NUM = 60 # pages
COMMON_HTML_FILENAME = "cetusk.page"
OUTPUT_LOG_FILENAME = "info.log"
```

## Execution

To load web page with dynamic contexts and save as HTML file.
```Bash
python3 extractor.py -m pull
```
Then `htmls` directory will be made and loaded HTML files ( `COMMON_HTML_FILENAME%d.html` ) are saved into.

To scrape the HTML file and dump scores as a log file.
```Bash
python3 extractor.py -m scrape
```
Then the parsed logging file ( `OUTPUT_LOG_FILENAME` ) are saved into the working directory.


# Analyze example

There is a simple example script for analyzing the log file. This script calculates a raw performance point ( PP ) and visualizes; supporting [the latest PP curve](https://www.patreon.com/posts/performance-34496939).

## ( Optional ) LaTeX

Install a TeX libraries to embed AMS Math font if you want.
```Bash
apt -y install dvipng texlive-base texlive-latex-extra cm-super texlive-lang-cjk texlive-fonts-recommended texlive-fonts-extra xdvik-ja
```
If you not use these libraries, some of lines are required to modify.

## Execution

Set `INPUT_LOG_FILENAME` for read the log file in the `analyze.py`, and execute.
```Bash
python3 analyze.py
```
Some adjustment of graph styles and ranges may be needed.