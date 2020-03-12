from unittest import TestCase
from ast import literal_eval

class Test(TestCase):

    def test_rdf2vec_light_array(self):
        """
        Simply testing the correct understanding of ast.
        """
        myArray = ["hello", "world"]
        myArrayString = str(myArray)
        myArrayBack = literal_eval(myArrayString)
        self.assertTrue(myArrayBack[0] == "hello" and myArrayBack[1] == "world")



