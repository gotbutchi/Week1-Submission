from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request

import requests
import re
import pandas as pd


app = Flask(__name__)
app.config['TESTING'] = True

def get_url(URL):
    """Get HTML from URL
    """
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

SEARCH_URL = "https://www.globalgiving.org/search/?size=10&keywords="
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
# table = pd.DataFrame(data, columns=['topic','title','author','description','link','image'])
# table.index = table.index + 1
# table.to_csv(f'{format_project_name}_list.csv', sep=',', encoding ='utf-8', index=False)

@app.route('/')
def index():
    data = crawl_globalgiving(BASE_URL)
    return render_template('home1.html', data=data)

@app.route('/search', methods=['POST','GET'])
def search():
    ''' using keyword from input in the form
    '''
    in_put = request.form['keywords']
    URL = SEARCH_URL + in_put.replace(' ','%20')
    result = crawl_globalgiving(URL)
    return render_template('search.html', result=result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 