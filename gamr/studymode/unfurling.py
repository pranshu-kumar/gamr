from bs4 import BeautifulSoup
import requests
import re


def OPG(url):
    source=requests.get(url).text
    soup=BeautifulSoup(source,'lxml')
    meta_tags_fb={}
    for meta in soup.find_all('meta'):
        try:
            content=meta['property']  
            pattern=re.compile(r'^og')
            matches=pattern.finditer(content)
            for match in matches:
                meta_tags_fb[meta['property'].split(':')[1]]=meta['content']        
        except Exception as e:
            pass
    return(meta_tags_fb)
