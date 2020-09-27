import requests


class ServiceAvailabilityCheck:
    """Class to check whether the server is fully functional. This class is not required to run the server.
    """

    def __init__(self, url):
        self.url = url
        self.success_sign = "\N{check mark} "
        self.failure_sign = "\N{cross mark} "

    def check_static_webpages(self):
        """Checks all static pages and prints a success or error message to the console.
        """
        print("Static Site Checks")
        print("------------------")
        self._check_single_page(self.url)
        self._check_single_page(self.url + "/index.html")
        self._check_single_page(self.url + "/api.html")
        self._check_single_page(self.url + "/contact.html")
        self._check_single_page(self.url + "/download.html")
        self._check_single_page(self.url + "/licenses.html")
        self._check_single_page(self.url + "/query.html")
        print("\n")

    def check_get_vector(self):
        """Checks the request: /rest/get-vector/<dataset>/<word>
        """
        print("Get Vector Checks")
        print("-----------------")
        self._check_single_vector_request(self.url + "/rest/get-vector/wordnet/car")
        self._check_single_vector_request(self.url + "/rest/get-vector/alod/car")
        self._check_single_vector_request(self.url + "/rest/get-vector/wiktionary/car")
        self._check_single_vector_request(self.url + "/rest/get-vector/dbpedia/Car")
        print("\n")

    def check_get_similarity(self):
        """Checks the request: /rest/get-similarity/<dataset>/<word>/<word>
        """
        print("Similarity Checks")
        print("-----------------")
        self._check_single_similarity_request(self.url + "/rest/get-similarity/alod/car/truck")
        self._check_single_similarity_request(self.url + "/rest/get-similarity/wiktionary/car/truck")
        self._check_single_similarity_request(self.url + "/rest/get-similarity/wordnet/car/truck")
        self._check_single_similarity_request(self.url + "/rest/get-similarity/dbpedia/car/truck")
        print("\n")

    def check_n_closest_concepts(self):
        print("N Closest Concept Checks")
        print("------------------------")
        self._check_single_cosest_concepts_request(self.url + "/rest/closest-concepts/dbpedia/10/Car")
        self._check_single_cosest_concepts_request(self.url + "/rest/closest-concepts/alod/10/car")
        self._check_single_cosest_concepts_request(self.url + "/rest/closest-concepts/wiktionary/10/car")
        self._check_single_cosest_concepts_request(self.url + "/rest/closest-concepts/wordnet/10/car")
        print("\n")

    def check_light_service_availability(self):
        print("Light Service")
        print("-------------")
        data = ["http://dbpedia.org/resource/Germany", "http://dbpedia.org/resource/Berlin"]
        data = {'entities': str(data)}
        url = self.url + '/rest/rdf2vec-light/dbpedia/250/cbow/2'
        result = requests.get(url, headers=data)
        if "http://dbpedia.org/resource/Germany" in result.text and "http://dbpedia.org/resource/Berlin" in result.text:
            print(self.success_sign + url)
        else:
            print(self.failure_sign + url)
        print("\n")

    def _check_single_cosest_concepts_request(self, url):
        result = requests.get(url)
        if "\"result\": [" in result.text and "\"concept\":" in result.text:
            print(self.success_sign + url)
        else:
            print(self.failure_sign + url)

    def _check_single_similarity_request(self, url):
        """Checks the response content of the given URL. Prints a success or error message to the console.

        Parameters
        ----------
        url : str
            URL to be checked.
        """
        result = requests.get(url)
        if "\"result\" :" in result.text:
            print(self.success_sign + url)
        else:
            print(self.failure_sign + url)

    def _check_single_vector_request(self, url):
        """Checks the response content of the given URL. Prints a success or error message to the console.

        Parameters
        ----------
        url : str
            URL to be checked.
        """

        result = requests.get(url)
        if "\"vector\": [" in str(result.content):
            print(self.success_sign + url)
        else:
            print(self.failure_sign + url)

    def _check_single_page(self, url):
        """Checks the HTTP status code of the given URL. Prints a success or error message to the console.

        Parameters
        ----------
        url : str
            URL to be checked.
        """

        response = requests.get(url)
        if response.status_code == 200:
            print(self.success_sign + url)
        else:
            print(self.failure_sign + url)


def main():
    #checker = ServiceAvailabilityCheck(url="http://www.kgvec2go.org")
    checker = ServiceAvailabilityCheck(url="http://0.0.0.0:5000")
    checker.check_static_webpages()
    checker.check_get_vector()
    checker.check_get_similarity()
    checker.check_light_service_availability()
    checker.check_n_closest_concepts()


if __name__ == '__main__':
    main()