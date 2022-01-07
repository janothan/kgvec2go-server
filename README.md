# KGvec2go Server
[![Unit Tests](https://github.com/janothan/kgvec2go-server/actions/workflows/tests.yml/badge.svg)](https://github.com/janothan/kgvec2go-server/actions/workflows/tests.yml)
[![Lint](https://github.com/janothan/kgvec2go-server/actions/workflows/black.yml/badge.svg)](https://github.com/janothan/kgvec2go-server/actions/workflows/black.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is the implementation of the *KGvec2go* server that powers the Web service (including the Web site): 
<a href="http://www.kgvec2go.org/">http://www.kgvec2go.org/</a>.
It is based on <a href="https://www.palletsprojects.com/p/flask/">flask</a> as well as 
<a href="https://radimrehurek.com/gensim/">gensim</a> and can be run with 
<a href="https://httpd.apache.org/">Apache HTTP Server</a>.

<!--Note that the walks were generated using project <a href="https://github.com/janothan/kgvec2go-walks">KGvec2go Walks</a>. -->

Do you want to train your own RDF2Vec embeddings? We recommend using <a href="https://github.com/dwslab/jrdf2vec">jRDF2Vec</a>.


## Development

### Coding Standards
- [black](https://github.com/psf/black) is used to format the project
- [numpy docstring](https://numpydoc.readthedocs.io/en/latest/format.html) is used to document code

### Administration
- The server is started by running `flask_server.py` (an option for local testing is available via `on_local=True`).
