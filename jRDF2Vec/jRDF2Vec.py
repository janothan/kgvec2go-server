import subprocess
import os
import io

class jRDF2Vec:
    """
    Class providing RDF2Vec Services
    """

    def __init__(self):
        """
        Constructor
        """
        self._port = 1024

    def train_light(self, entities, number_of_walks, mode, dimension):

        # increment the port number for the request
        current_port = self._increment_port()

        # create directory
        directory_name = "./jRDF2Vec/models/" + str(current_port) + "/"
        try:
            os.makedirs(directory_name)
        except OSError:
            pass
        directory_name = os.path.realpath(directory_name) + "/"

        walk_directory_name = directory_name + "walks/"
        try:
            os.makedirs(walk_directory_name)
        except OSError:
            pass
        walk_directory_name = os.path.realpath(walk_directory_name) + "/"

        # write entities to file
        entity_file_name = directory_name + "entities.txt"
        with io.open(entity_file_name, 'w', encoding='utf8') as f:
            text = ""
            for entity in entities:
                text += entity + "\n"
            f.write(text)

        subprocess.check_output(['java', "-jar", "./jRDF2Vec/jRDF2Vec.jar", "-light", entity_file_name, "-graph",
                                          "./jRDF2Vec/dbpedia_merged.hdt", "-numberOfWalks", str(number_of_walks),
                                         "-trainingMode", str(mode), "-dimension", str(dimension), "-walkDir", walk_directory_name])

        result = {}
        with open(walk_directory_name + "model.txt", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                line = line.strip(" ")
                line = line.split(" ")
                result[line[0]] = [float(i) for i in line[1:]]

        return result

    def _increment_port(self):
        """
        Increases the port number.

        Returns
        -------
            nothing
        """
        if self._port == 65535:
            self._port = 1024
        else:
            self._port += 1
        return self._port

