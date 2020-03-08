from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for

import requests
import re


app = Flask(__name__)
app.config['TESTING'] = True

# r = requests.get('https://www.globalgiving.org/search/?size=25&nextPage=1&sortField=sortorder&loadAllResults=true')

def get_url(URL):
    """Get HTML from URL
    """
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

HOME_URL = 'https://www.globalgiving.org'
BASE_URL = 'https://www.globalgiving.org/search/?size=25&nextPage=1&sortField=sortorder&loadAllResults=true'

def crawl_globalgiving(URL):
    soup = get_url(URL)
    articles = soup.find_all('div', class_="flex_growChildren")
    data = []
    for article in articles:
        d = {'topic':'','title':'', 'author':'','link':'', 'image':'', 'description':''}
        d['topic'] = article.span.text.replace('\n','').replace("               ", ' ').strip()
        d['title'] = article.h4.text.strip()
        d['author'] = article.find('div', class_="grid-12 box_verticalPaddedHalf").text.strip()
        d['description'] =  article.find('div', class_="col_ggSecondary1Text").text.split('…')[0].strip() + '..'
        d['link'] =  HOME_URL + article.a["href"]
        d['image'] = HOME_URL + article.a["style"][article.a["style"].find("(")+1:article.a["style"].rfind(");")]
        data.append(d)  
    return data

@app.route('/')
def index():
    data = crawl_globalgiving(BASE_URL)
    return render_template('home1.html', data=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 