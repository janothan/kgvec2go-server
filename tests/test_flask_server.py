from ast import literal_eval


class Test:

    def test_rdf2vec_light_array(self):
        """
        Simply testing the correct understanding of ast.
        """
        my_array = ["hello", "world"]
        my_array_string = str(my_array)
        my_array_back = literal_eval(my_array_string)
        assert my_array_back[0] == "hello" and my_array_back[1] == "world"
