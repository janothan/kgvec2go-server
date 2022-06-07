from typing import Union, List

from flask import Flask, render_template, request
from ast import literal_eval
import logging
import sys
import platform

from gensim.models import KeyedVectors

from kgvec2go_server.alod.alod_query_service import AlodQueryService
from kgvec2go_server.dbnary.dbnary_query_service import DbnaryQueryService
from kgvec2go_server.dbpedia.dbpedia_query_service import DBpediaQueryService
from kgvec2go_server.generic.generic_linker import GenericDBpediaLinker
from kgvec2go_server.generic.generic_query_service import GenericKvQueryService
from kgvec2go_server.jRDF2Vec.jRDF2Vec import jRDF2Vec
from kgvec2go_server.wordnet.wordnet_query_service import WordnetQueryService

# set manually if you do not have a mac:
on_local = "macOS" in platform.platform()
local_port = 5001  # apple now uses 5000 for airplay


if on_local:
    logging.basicConfig(
        handlers=[
            logging.FileHandler(__file__ + ".log", "w", "utf-8"),
            logging.StreamHandler(),
        ],
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.DEBUG,
    )
else:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

app = Flask(__name__)
logging.info("Initiating Server...")


@app.route("/index.html")
@app.route("/about.html")
@app.route("/")
def show_start_page():
    return render_template("about.html")


@app.route("/query.html")
def show_query_page():
    return render_template("query.html")


@app.route("/licenses.html")
def show_licenses_page():
    return render_template("licenses.html")


@app.route("/download.html")
def show_download_page():
    return render_template("download.html")


@app.route("/api.html")
def show_api_page():
    return render_template("api.html")


@app.route("/contact.html")
def show_about_page():
    return render_template("contact.html")


@app.route("/robots.txt")
def robots_txt():
    return render_template("robots.txt")


generic_services: List[GenericKvQueryService] = []
"""A list of generic services running in the backend.
"""

if on_local:
    logging.info("Using local environment.")

    """
    logging.info("Init DBpediaQueryService")
    path_to_dbpedia_vectors = "/Users/janportisch/Documents/Data/KGvec2go_DBpedia_Optimized/sg200_dbpedia_500_8_df_vectors_reduced.kv"
    # path_to_dbpedia_entities = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/dbpedia/dbpedia_entities.txt"
    path_to_dbpedia_redirects = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/dbpedia/redirects_en.ttl"
    # dbpedia_service = DBpediaQueryService(
    #    vector_file=path_to_dbpedia_vectors, redirect_file=path_to_dbpedia_redirects
    # )
    logging.info("DBpediaQueryService Initialized.")

    # dbpedia_service = DBpediaQueryService(entity_file=path_to_dbpedia_entities, vector_file=path_to_dbpedia_vectors, redirect_file=path_to_dbpedia_redirects)
    alod_service = 0
    wordnet_service = 0

    logging.info("Init WordnetQueryService")
    path_to_wordnet_vectors = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/wordnet/sg200_wordnet_500_8_df_mc1_it3_reduced_vectors.kv"
    path_to_wordnet_entities = "/Users/janportisch/Documents/PhD/LREC_2020/Language_Models/wordnet/wordnet_entities.txt"
    # wordnet_service = WordnetQueryService(
    #    entity_file=path_to_wordnet_entities,
    #    vector_file=path_to_wordnet_vectors,
    #    is_reduced_vector_file=True,
    # )
    logging.info("WordnetQueryService initialized.")

    dbnary_service = 0
    # rdf_2_vec = jRDF2Vec()
    """

    transe_dbpedia_vectors_path: str = (
        "/Users/janportisch/Downloads/transeL2-all-dbpedia.kv"
    )
    transe_dbpedia_vectors: KeyedVectors = KeyedVectors.load(
        transe_dbpedia_vectors_path, mmap="r"
    )

    transe_linker: GenericDBpediaLinker = GenericDBpediaLinker(
        kv=transe_dbpedia_vectors
    )
    transe_service: GenericKvQueryService = GenericKvQueryService(
        kv=transe_dbpedia_vectors,
        linker=transe_linker,
        dataset="DBpedia",
        dataset_version="2021-09",
        model="transe",
        model_version="v1",
    )

    generic_services.append(transe_service)

    logging.info("KGvec2go Operational")

else:
    logging.info("Using server environment.")

    # ~~~ WordNet ~~~
    path_to_wordnet_model = "/disk/wordnet/sg200_wordnet_100_8_df_mc1_it3"
    path_to_wordnet_entities = "/disk/wordnet/wordnet_entities.txt"

    # wordnet_service = 0
    wordnet_service = WordnetQueryService(
        entity_file=path_to_wordnet_entities,
        model_file=path_to_wordnet_model,
        is_reduced_vector_file=False,
    )
    logging.info("WordNet service initiated.")

    # ~~~ ALOD ~~~
    path_to_alod_vectors = "/disk/alod/sg200_alod_100_8_df_mc1_it3_vectors.kv"

    # alod_service = 0
    alod_service = AlodQueryService(vector_file=path_to_alod_vectors)
    logging.info("ALOD service initiated.")

    # ~~~ DBpedia ~~~
    path_to_dbpedia_vectors = "/disk/dbpedia/api_vectors/v2/model.kv"
    # path_to_dbpedia_redirects = "/disk/dbpedia/redirects_en.ttl"
    dbpedia_service = DBpediaQueryService(
        vector_file=path_to_dbpedia_vectors, redirect_file=""
    )
    logging.info("DBpedia service initiated.")

    # ~~~ DBnary / Wiktionary ~~~
    path_to_dbnary_vectors = "/disk/dbnary/sg200_dbnary_100_8_df_mc1_it3_vectors.kv"
    path_to_dbnary_entities = "/disk/dbnary/dbnary_entities.txt"

    # dbnary_service = 0
    dbnary_service = DbnaryQueryService(
        entity_file=path_to_dbnary_entities, vector_file=path_to_dbnary_vectors
    )
    logging.info("Wiktionary service initiated.")

    rdf_2_vec = jRDF2Vec(
        jrdf_2_vec_directory="/mnt/disk/server/EmbeddingServer/jRDF2Vec/"
    )
    print("RDF2Vec Service initiated")

    logging.info("KGvec2go Operational")

logging.info("Server Initiated.")


@app.route("/rest/rdf2vec-light/<data_set>/<walks>/<mode>/<dimension>", methods=["GET"])
def rdf2vec_light(data_set, walks, mode, dimension):
    # sanity check:
    if data_set.lower() != "dbpedia":
        print("Only DBpedia allowed")
        return None
    if request is None:
        print("none")
    entities = request.headers.get("entities")
    if entities is None:
        print("ERROR: Entities are missing in header.")
        return None
    entities = literal_eval(entities)
    result = rdf_2_vec.train_light(
        entities=entities, number_of_walks=walks, mode=mode, dimension=dimension
    )
    return result


@app.route(
    "/rest/v2/closest-concepts/<dataset>/<dataset_version>/<model>/<model_version>/<int:top_n>/<concept_name>",
    methods=["GET"],
)
def closest_concepts(
    dataset: str,
    dataset_version: str,
    model: str,
    model_version: str,
    top_n: int,
    concept_name: str,
) -> Union[None, str]:
    service = GenericKvQueryService.get_service_from_list(
        the_list=generic_services,
        dataset=dataset,
        dataset_version=dataset_version,
        model=model,
        model_version=model_version,
    )
    if service is None:
        logging.error(
            f"No embedding configuration found for: {dataset}/{dataset_version}/{model}/{model_version}"
        )
        return '{"error": "No embedding found for model/dataset combination."}'
    else:
        return service.get_closest_concepts_json(label=concept_name, topn=int(top_n))


@app.route(
    "/rest/v2/addition-closest-concepts/<dataset>/<dataset_version>/<model>/<model_version>/<int:top_n>/<concept_name_1>/<concept_name_2>",
    methods=["GET"],
)
def addition_closest_concepts(
    dataset: str,
    dataset_version: str,
    model: str,
    model_version: str,
    top_n: int,
    concept_name_1: str,
    concept_name_2: str,
) -> Union[None, str]:
    service = GenericKvQueryService.get_service_from_list(
        the_list=generic_services,
        dataset=dataset,
        dataset_version=dataset_version,
        model=model,
        model_version=model_version,
    )
    if service is None:
        logging.error(
            f"No embedding configuration found for: {dataset}/{dataset_version}/{model}/{model_version}"
        )
        return '{"error": "No embedding found for model/dataset combination."}'
    else:
        return service.most_similar_addition_json(
            label_1=concept_name_1, label_2=concept_name_2, topn=int(top_n)
        )


@app.route("/rest/closest-concepts/<data_set>/<top_n>/<concept_name>", methods=["GET"])
def closest_concepts_legacy(data_set, top_n, concept_name) -> Union[None, str]:
    """Legacy method (no model version, no dataset, no dataset version)

    Parameters
    ----------
    data_set : str
    top_n : str
        Integer as string.
    concept_name : str
        Concept name.

    Returns
    -------
    str
    JSON message.
    """
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == "wiktionary":
        print("Wiktionary closest-concepts query fired.")
        result = dbnary_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == "wordnet":
        print("Wordnet closest-concepts query fired.")
        result = wordnet_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == "alod":
        print("ALOD Classic closest-concepts query fired.")
        result = alod_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    elif data_set == "dbpedia":
        print("DBpedia closts-concepts query fired.")
        result = dbpedia_service.find_closest_lemmas(concept_name, top_n)
        print(result)
        return result
    return None


@app.route(
    "/rest/v2/get-vector/<dataset>/<dataset_version>/<model>/<model_version>/<concept_name>",
    methods=["GET"],
)
def get_vector(dataset, dataset_version, model, model_version, concept_name):
    service = GenericKvQueryService.get_service_from_list(
        the_list=generic_services,
        dataset=dataset,
        dataset_version=dataset_version,
        model=model,
        model_version=model_version,
    )
    if service is None:
        logging.error(
            f"No embedding configuration found for: {dataset}/{dataset_version}/{model}/{model_version}"
        )
        return '{"error": "No embedding found for model/dataset combination."}'
    else:
        return service.get_vector_json(label=concept_name)


@app.route("/rest/get-vector/<data_set>/<concept_name>", methods=["GET"])
def get_vector_legacy(data_set, concept_name):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == "wiktionary":
        print("Wiktionary get-vector query fired.")
        result = dbnary_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == "wordnet":
        print("WordNet get-vector query fired.")
        result = wordnet_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == "alod":
        print("ALOD Classic get-vector query fired.")
        result = alod_service.get_vector(concept_name)
        print(result)
        return result
    elif data_set == "dbpedia":
        print("DBpedia get-vector query fired.")
        result = dbpedia_service.get_vector(concept_name)
        print(result)
        return result
    return None


@app.route(
    "/rest/get-similarity/<data_set>/<concept_name_1>/<concept_name_2>", methods=["GET"]
)
def get_similarity(data_set, concept_name_1, concept_name_2):
    data_sets = ["wordnet", "wiktionary", "babelnet", "alod", "dbpedia"]
    data_set = data_set.lower()
    if data_set not in data_sets:
        return None
    if data_set == "wiktionary":
        print("Wiktionary get-vector query fired.")
        result = dbnary_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result
    elif data_set == "wordnet":
        print("Wordnet get-vector query fired.")
        result = wordnet_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result
    elif data_set == "alod":
        print("ALOD Classic get-similarity query fired.")
        result = alod_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result
    elif data_set == "dbpedia":
        print("DBpedia get-similarity query fired.")
        result = dbpedia_service.get_similarity_json(concept_name_1, concept_name_2)
        print(result)
        return result


if on_local:
    app.run(host="0.0.0.0", port=local_port, debug=False)


if __name__ == "__main__":
    pass
