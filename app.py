from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# DATABASE_URL is by default
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('votes', lazy='dynamic'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('votes', lazy='dynamic'))


@app.route('/donate', methods=['GET', 'POST'])
def homepage():
    message = None
    message_level = ''
    if request.method == 'POST':
        email = request.form.get('email')
        project_id = request.form.get('project')
        if email and project_id:
            user = db.session.query(User).filter_by(email=email).first()
            if user:
                message_level = 'info'
                message = 'You have already voted!'
            else:
                user = User(email=email)
                db.session.add(user)
                project = db.session.query(Project).filter_by(id=project_id).first()
                vote = Vote(user=user, project=project)
                db.session.add(vote)
                db.session.commit()
                message_level = 'success'
                message = 'Your vote for {} has been submitted!'.format(project.name)
        else:
            message_level = 'danger'
            message = 'You must enter your email and select a project to cast a vote.'

    projects = Project.query.order_by('id').all()
    total_votes = db.session.query(Vote).count()
    vote_query = db.session.query(Vote.project_id, func.count(Vote.project_id))
    vote_counts = vote_query.group_by(Vote.project_id).order_by('project_id').all()


    projects = Project.query.all()

    return render_template('index.html', message=message, message_level=message_level,
                           projects=projects, total_votes=total_votes, vote_counts=vote_counts)



from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request

import requests
import re
import pandas as pd

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
    app.run(debug=True)
