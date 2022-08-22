import os
import time
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

SOURCE_URL = "https://scoresaber.com/u/76561198993766763"
WAIT_AJAX_INTERVAL = 10.0 # seconds
MAX_PAGE_NUM = 60 # pages
COMMON_HTML_FILENAME = "cetusk.page"
OUTPUT_LOG_FILENAME = "info.log"

def createDriver ():
    # ref: https://stackoverflow.com/a/53073789
    options = Options ()
    options.add_argument ( "--headless" )
    options.add_argument ( "--no-sandbox" )
    options.add_argument ( "--disable-dev-shm-usage" )

    # ref: https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/#3-hard-coded-location
    service = Service ( executable_path="./chromedriver" )

    # DeprecationWarning: use options instead of chrome_options
    return webdriver.Chrome ( service=service, options=options )

def getSource ( driver:webdriver.Chrome, url:str, wait_interval:float=10.0 ):
    driver.get ( url )
    # wait completing of a load ajax
    time.sleep ( wait_interval )
    return driver.page_source.encode ( "utf-8" )

def pullHtml ( source_url:str, max_page_num:int, wait_ajax_interval:float, out_common_file_name:str ):
    driver = createDriver ()
    os.makedirs ( "htmls" )
    for page in range ( 1, max_page_num+1 ):
        print ( "[MAIN] Process %d / %d:" % ( page, max_page_num ) )
        print ( "           Accessing web page ..." )
        dom = getSource (
            driver=driver,
            url="%s?page=%d&sort=top" % ( source_url, page ),
            wait_interval=wait_ajax_interval
        )
        print ( "           Accessing web page ... OK" )
        # save for test
        print ( "           Dump DOM ..." )
        with open ( "htmls/%s%d.html" % ( out_common_file_name, page ), "w" ) as fh:
            fh.write ( driver.page_source )
        print ( "           Dump DOM ... OK" )
    driver.quit ()

def scrapeHtml ( common_file_name:str, max_page_num:int, out_file_name:str="info.log" ):
    rankCount = 0
    for page in range ( 1, max_page_num+1 ):
        print ( "[MAIN] Process %d / %d:" % ( page, max_page_num ) )
        print ( "           Read %s%d.html ..." % ( common_file_name, page ) )

        dom = b""
        with open ( "htmls/%s%d.html" % ( common_file_name, page ), "r" ) as fh:
            dom = fh.read ()
        
        # whole context
        soup = BeautifulSoup ( dom, "html5lib" )

        # extract class names
        svelteClasses = []
        div = soup.find ( "div", id="svelte" )
        div ( "div", class_=lambda c: svelteClasses.append ( c ) )

        # memorize target hashes of each class name
        rootClass = None
        rankingClassHash = None
        songClassHash = None
        scoreClassHash = None
        for _class in svelteClasses:
            if _class is None: continue
            if "window has-shadow noheading bottomSection svelte" in _class:
                rootClass = _class
            if "table-item svelte" in _class:
                rankingClassHash = _class.split ( "-" )[ -1 ]
            if "song-image-wrapper svelte" in _class:
                songClassHash = _class.split ( "-" )[ -1 ]
            if "scoreInfo svelte" in _class:
                scoreClassHash = _class.split ( "-" )[ -1 ]

        # check
        # print ( "           Ranking class hash ... %s" % rankingClassHash )
        # print ( "           Song class hash ... %s" % songClassHash )
        # print ( "           Score class hash ... %s" % scoreClassHash )

        # extract my ranking tables
        div = soup.find ( "div", class_=rootClass )

        # top scores    
        tables = div.find_all ( "div", class_="table-item svelte-%s" % rankingClassHash )

        # loop for maps
        writeLines = ""
        if page == 1:
            writeLines = "rank,difficulty,star,acc,pp_raw,pp_eff,weight,mod,name,artist,mapper\n"     
        for elm in tables:
            contexts = elm.find_all ( "div", class_="svelte-%s" % rankingClassHash )

            # ranking: e.g. "#1,234" --> ["", "1,234"] --> ["1", "234"] --> "1234" --> 1234
            ctx_rank = contexts [ 1 ].find ( "div", class_="rank-info svelte-%s" % rankingClassHash )
            ctx_rank = ctx_rank.find ( "a", class_="svelte-%s" % rankingClassHash )
            rank = int ( "".join ( ctx_rank.text.split ( "#" )[ 1 ].split ( "," ) ) )

            # song
            ctx_song_level = contexts [ 5 ].find ( "div", class_="song-image-wrapper svelte-%s" % songClassHash ).find ( "div" )
            difficulty = ctx_song_level.get ( "title" )
            ctx_song_star = ctx_song_level.text  # [float][star] or [string]
            if ctx_song_star in [ "E", "N", "H", "X", "Ex+" ]:
                star = -1.0
            else:
                star = float ( ctx_song_star [ : -1 ] )
            
            ctx_song_title = contexts [ 5 ].find ( "div", class_="song-info-container mobile-enhance svelte-%s" % songClassHash )
            title = ctx_song_title.find ( "div", class_="song-info svelte-%s" % songClassHash ).find_all ( "span" )
            name = title [ 0 ].text
            artist = title [ 1 ].text
            mapper = ctx_song_title.find ( "div", class_="mapper-info" ).find ( "span", class_="mapper-name" ).text

            # score
            ctx_score = contexts [ 6 ].find ( "div", class_="scoreInfo svelte-%s" % scoreClassHash )
            ctx_score_acc = ctx_score.find ( "span", class_="stat acc svelte-%s" % scoreClassHash )
            pp_raw = -1.0; pp_eff = -1.0; weight = -1.0
            if ctx_score_acc is None:
                acc = -1.0
            else:
                acc = float ( ctx_score_acc.text [ : -1 ] ) # remove "%"

                # performance point
                ctx_score_pp = ctx_score.find ( "div", class_="stat ranked svelte-%s" % scoreClassHash )
                if ctx_score_pp is None:
                    pp_raw = -1.0; pp_eff = -1.0; weight = -1.0; mod = "None"
                else:
                    ctx_score_pp_raw = ctx_score_pp.find ( "span", class_="info svelte-%s" % scoreClassHash )
                    ctx_score_pp_eff = ctx_score_pp.find ( "span", class_="small info svelte-%s" % scoreClassHash )
                    # parse
                    pp_raw = float ( ctx_score_pp_raw.text [ : -2 ] ) # remove "pp"
                    pp_eff = float ( ctx_score_pp_eff.text [ 1 : -3 ] ) # remove "[" and "pp]"
                    weight = float ( ctx_score_pp_eff.get ( "title" ).split ()[ 1 ][ : -1 ] ) # remove "Weighted " and "%"

            # modifier
            ctx_score_mod = ctx_score.find ( "span", class_="stat hide-details svelte-%s" % scoreClassHash )
            mod = "None"
            if ctx_score_mod is not None:
                mod = ctx_score_mod.text
            else:
                mod = "None"

            # write out
            rankCount += 1
            # rank, difficulty, star, acc, pp_raw, pp_eff, weight, name, artist, mapper
            writeLines += "%d,%s,%.2f,%.2f,%.2f,%.2f,%.2f,%s,%s,%s,%s\n" % (
                rankCount, difficulty, star, acc, pp_raw, pp_eff, weight, mod, name, artist, mapper
            )

        writeMode = "a"
        if page == 1: writeMode = "w"
        with open ( out_file_name, writeMode ) as fh:
            fh.write ( writeLines )

if __name__ == "__main__":

    parser = argparse.ArgumentParser ()
    parser.add_argument (
        "-m", "--mode",
        type=str, required=True,
        choices=[ "pull", "scrape" ],
        help="Mode pulling from web or scraping from downloaded file"
    )
    args = parser.parse_args ()

    # Access web page and download as html files.
    if args.mode == "pull":
        pullHtml (
            source_url=SOURCE_URL,
            max_page_num=MAX_PAGE_NUM,
            wait_ajax_interval=WAIT_AJAX_INTERVAL,
            out_common_file_name=COMMON_HTML_FILENAME
        )
        print ( "[MAIN] Process completed." )
    # Scrape downloaded html files and dump a log file.
    elif args.mode == "scrape":
        scrapeHtml (
            common_file_name=COMMON_HTML_FILENAME,
            max_page_num=MAX_PAGE_NUM,
            out_file_name=OUTPUT_LOG_FILENAME
        )
        print ( "[MAIN] Process completed." )
    else:
        print ( "ERROR: unexpected input." )
        sys.exit ()




