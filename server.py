import flask
app = flask.Flask(__name__)

import glob
import json

data = json.load(open('notes.json'))
keys = {}
for entry in data['notes']:
    keys[entry['id']] = entry

papers = []
for paper in glob.glob('text/papers/*'):
    paperid = paper
    paperid = paperid.split('id=')[1]
    paperid = paperid.split('.txt')[0]
    papers.append([paperid, open(paper, encoding='utf-8', errors='ignore').read()])
papers = sorted(papers)
print('Loaded {} papers'.format(len(papers)))

from reviewer import ratings, sorted_papers

@app.route("/")
def index():
    query = 'Top 100 papers'
    found = []
    for paperid, paper in papers:
        if paperid in sorted_papers[-100:]:
            if paperid in keys:
                try:
                    rank = sorted_papers.index(paperid)
                    pct = int(100 * rank / len(sorted_papers))
                except ValueError as e:
                    rank = None
                    pct = None
                d = dict(id=paperid, title=keys[paperid]['content']['title'], data=keys[paperid], rating=ratings[paperid], rank=rank, pct=pct)
                found.append(d)
    found = sorted(found, key=lambda x: x['rank'], reverse=True)
    return flask.render_template('base.html', query=query, results=found, total_papers=len(sorted_papers))

@app.route("/search/")
def search(query=None):
    query = query if query else flask.request.args.get('query')
    found = []
    for paperid, paper in papers:
        if query.lower() in paper.lower():
            print(paperid)
            if paperid in keys:
                try:
                    rank = sorted_papers.index(paperid)
                    pct = int(100 * rank / len(sorted_papers))
                except ValueError as e:
                    rank = None
                    pct = None
                d = dict(id=paperid, title=keys[paperid]['content']['title'], data=keys[paperid], rating=ratings[paperid], rank=rank, pct=pct)
                found.append(d)
    found = sorted(found, key=lambda x: x['rank'] or 1e6, reverse=True)
    return flask.render_template('base.html', query=query, results=found, total_papers=len(sorted_papers))
