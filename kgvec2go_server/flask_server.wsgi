#! /usr/bin/python3111

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/disk/server/EmbeddingServer/")
sys.path.insert(0, "/disk/server/EmbeddingServer/kgvec2go-server/")
sys.path.insert(0, "/disk/server/EmbeddingServer/kgvec2go-server/kgvec2go_server")
from flask_server import app as application

application.secret_key = "anything you wish"
