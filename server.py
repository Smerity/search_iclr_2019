import flask
app = flask.Flask(__name__)

import glob
import json
import random

from collections import Counter

data = json.load(open('notes.json'))
keys = {}
for entry in data['notes']:
    keys[entry['id']] = entry

tags = Counter()
for key, value in keys.items():
    paper_tags = [x.lower() for x in value['content']['keywords']]
    tags.update(paper_tags)
print('Loaded {} tags'.format(len(tags)))

papers = []
for paper in glob.glob('text/papers/*'):
    paperid = paper
    paperid = paperid.split('id=')[1]
    paperid = paperid.split('.txt')[0]
    paper_text = open(paper, encoding='utf-8', errors='ignore').read()
    # Add tags to the end for the primitive search
    if paperid in keys:
        paper_tags = keys[paperid]['content']['keywords']
        #print(paper_tags)
        paper_text += ' ' + ' '.join(paper_tags)
    papers.append([paperid, paper_text])
papers = sorted(papers)
print('Loaded {} papers'.format(len(papers)))

from reviewer import ratings, sorted_papers

def get_random_tags(n=5):
    return set(random.choice(list(tags.keys())) for _ in range(n))

@app.route("/")
def index():
    query = "Random selection"
    found = []
    for paperid, paper in papers:
        if paperid in keys:
            d = dict(id=paperid, title=keys[paperid]['content']['title'], data=keys[paperid], rating=ratings[paperid], rank=None, pct=None)
        found.append(d)
    random.shuffle(found)
    found = found[:100]
    random_tags = get_random_tags()
    return flask.render_template('results.html', query=query, results=found, total_papers=len(sorted_papers), random_tags=random_tags)

@app.route("/search/")
def search(query=None):
    query = query if query else flask.request.args.get('query')
    if query is None:
        return flask.redirect(flask.url_for('index'))
    found = []
    for paperid, paper in papers:
        if query.lower() in paper.lower():
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
    random_tags = get_random_tags()
    return flask.render_template('results.html', query=query, results=found, total_papers=len(sorted_papers), random_tags=random_tags)

@app.route('/tags/')
def all_tags():
    return flask.render_template('tags.html', tags=tags)
