import mechanize,json,re
from lxml import etree
from StringIO import StringIO
import glob,sys,pdb
import time
import urlparse
import writing_to_file
import logging
import argparse
import ConfigParser

def get_logger(name=u'log'):
    logger = logging.getLogger(name)
    hdlr = logging.FileHandler(name + u'.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger()

def googlesearch(br,key):
    count = 2
    try:
        br.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')] 
        br.set_handle_referer(False)
        br.set_handle_robots(False)
        br.set_handle_equiv(False)
        try:
            br.open('http://www.google.com/advanced_search') 
        except mechanize.URLError,e:
            print "Failed to open the URL"
            msg = "Failed to open the URL"
            logger.error('%s Because of %s',msg,e)
            exit(1)
        #print [form for form in br.forms()][0]
        br.select_form(name='f')   
        br.form['as_q'] = key
        data = br.submit()
    except mechanize.HTTPError,e:
        print "Got error code",e.code
        logger.error(e)
        exit(1)
    content = data.read()
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(content), parser)	
    urls = tree.xpath('//h3/a/@href')                 ##Fetching the first page links
    links = []

  
    ##Extract only the main link from the complete url
    for url in urls:
        #links.append(re.findall(r'/url\?q=(http://[^&]*)', url)) 
        try:
            temp = urlparse.parse_qs(urlparse.urlparse(url).query)
            if 'q' in temp:
                extractedurl = temp['q'][0]
            else:
                continue
        except KeyError,e:
            raise URLError('No q')
            logger.error(e)
        #links.append(re.findall(r'/url\?q=(http://.*)&sa=.*', url))
        links.append(extractedurl)
    #next_url = tree.xpath('//*[@id="nav"]/tr/td/a/@href')

    #Getting the subsequent links from the next pages 
    count = 1
    while(count < 10):
        count = count+1
        try:
            f = br.find_link(text=str(count))
            req = br.click_link(text=str(count))
            #br.open("http://www.google.com"+request)
            #follow_content = br.response().read()
            #follow_content = response().read()
            br.open(req)
            res = br.response().read()
            tree1 = etree.parse(StringIO(res), parser)
            follow_urls = tree1.xpath('//h3/a/@href')
            for followurl in follow_urls:
                #links.append(re.findall(r'/url\?q=(http://.*)&sa=.*', followurl))
                try:
                    tempurl = urlparse.parse_qs(urlparse.urlparse(followurl).query)
                    if 'q' in tempurl:
                        finalurl = tempurl['q'][0]
                    else:
                        continue
                except KeyError,e:
                    raise URLError('No q')
                    logger.error(e)
                links.append(finalurl)
                #links.add(finalurl)
        except mechanize.LinkNotFoundError,e:
            print "Reached the maximum page: ",count
            logger.error(e)
            break
    print "Total links extracted:",len(links)

    ##Writing the extracted links to a file
    writing_to_file.write_to_file(key,links)        
   

def keyword_read(br):
    #path = '/home/vinothini/projects/virtualenvs/scrape_links/keywords/*.txt'
    config = ConfigParser.RawConfigParser()
    config.read('links.cfg')
    path = config.get('section1','filepath')
    #print path
    files=glob.glob(path)
    print files
    global i
    i = 0
    for name in files:    
        f=open(name, 'r')
        i = i+1
        keyword = f.readlines()
        new_keyword = ''.join(keyword)
        print "Name of file read : ",name
        print "Keywords :", new_keyword 
        googlesearch(br,new_keyword)
        f.close()
    print "Total Number of files read= ",i



    
if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--q",help="query to search",
                        type=str)
    args = parser.parse_args()
   
    try:
        br = mechanize.Browser(factory=mechanize.RobustFactory()) 
        if args.q:
            print "Keyword: ",args.q
            googlesearch(br,args.q)
        else:
            keyword_read(br)
    except mechanize.HTTPError,e:
        print "Got error code",e.code
        logger.error("HTTP Error")
   
    run_time = time.time()-start
    print "It took",run_time ,"for files",i

