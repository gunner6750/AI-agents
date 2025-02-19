from flask import Flask, render_template, url_for
import requests
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import os
import arxiv
import random
def get_AI_papers(num):
  """
  Retrieves AI papers from Arxiv.

  Args:
      num: The number of papers to retrieve.

  Returns:
      A list of paper entries (BeautifulSoup Tag objects).
  """
  # Use arxiv library for queries
  search = arxiv.Search(
      query="AI",
      max_results=num,  # Set the desired number of results
      sort_by=arxiv.SortCriterion.SubmittedDate
  )

  # Extract paper information and store in a list
  #id is a random big number
  
  papers = []
  for result in search.results():
      authors =','.join([str(author) for author in result.authors])
      paper_entry = {
          'title': result.title,
          'authors': authors,
          'abstract': result.summary,
          'date': result.published,
          'pdf_url': result.pdf_url
      }
      papers.append(paper_entry)  

  return papers
def store_paper(paper):
  """
  Store a paper entry in the database.

  Args:
      paper: A dictionary containing the paper information.
  """
  # Create a new Paper object
  new_paper = Paper(
      title=paper['title'],
      authors=paper['authors'],
      summary=paper['abstract'],
      date=paper['date'],
      link=paper['pdf_url']
  )

  # Add the new paper to the database session
  db.session.add(new_paper)
  db.session.commit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'papers.db')
db = SQLAlchemy(app)

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=True)

with app.app_context():
    db.create_all()

def fetch_and_store_papers():
    papers = get_AI_papers(50)
    for paper in papers:
        store_paper(paper)
@app.route('/')
def index():
    NEWS_API_KEY = "c527dfb68be1438895522dc8e6801608"  # Replace with your actual News API key
    vietnamese_news_list = []
    international_news_list = []
    try:
        vietnamese_news_url = f"https://newsapi.org/v2/top-headlines?country=vn&apiKey={NEWS_API_KEY}"
        response = requests.get(vietnamese_news_url)
        response.raise_for_status()
        data = response.json()
        for article in data['articles']:
            vietnamese_news_list.append({
                'title': article['title'],
                'snippet': article['description'] or article['content'] or ''
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Vietnamese news: {e}")

    try:
        international_news_url = f"https://newsapi.org/v2/top-headlines?q=international&apiKey={NEWS_API_KEY}"
        response = requests.get(international_news_url)
        response.raise_for_status()
        data = response.json()
        for article in data['articles']:
            international_news_list.append({
                'title': article['title'],
                'snippet': article['description'] or article['content'] or ''
            })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching international news: {e}")

    papers = Paper.query.order_by(Paper.date.desc()).limit(10).all()
    return render_template('index.html', vietnamese_news=vietnamese_news_list, international_news=international_news_list, papers=papers)

@app.route('/fetch_papers')
def fetch_papers_route():
    fetch_and_store_papers()
    return "Papers fetched and stored!"

    return render_template('index.html', news=news_list, papers=paper_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=58158)