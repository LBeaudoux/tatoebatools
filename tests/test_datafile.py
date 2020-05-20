import unittest
from io import StringIO

from tatoebatools.datafile import unsplit_field, custom_reader


class TestUnsplitField(unittest.TestCase):
    
    def test_without_split_field(self):
        row = ["foobar", "text not split by delimiters"]
        unsplit_row = unsplit_field(
            row, nb_cols=2, delimiter=",", index_field=-1
        )
        self.assertEqual(unsplit_row, row)

    def test_with_end_split_field(self):
        nok_row = ["foobar", "text", " split", " by", " delimiters"]
        ok_row = ["foobar", "text, split, by, delimiters"]
        unsplit_row = unsplit_field(
            nok_row, nb_cols=2, delimiter=",", index_field=-1
        )
        self.assertEqual(unsplit_row, ok_row)

    def test_with_midlle_split_field(self):
        nok_row = ["foobar", "text", " split", " by", " delimiters", "foo"]
        ok_row = ["foobar", "text, split, by, delimiters", "foo"]
        unsplit_row = unsplit_field(
            nok_row, nb_cols=3, delimiter=",", index_field=1
        )
        self.assertEqual(unsplit_row, ok_row)    


class TestCustomReader(unittest.TestCase):

    def test_with_commas(self):
        str_io = StringIO("a,b,c\n")
        rows = [row for row in custom_reader(str_io, ",", -1)]

        self.assertEqual(rows, [["a", "b", "c"]])       

    def test_with_multiple_rows(self):
        str_io = StringIO("a,b,c\nd,e,f\n")
        rows = [row for row in custom_reader(str_io, ",", -1)]

        self.assertEqual(rows, [["a", "b", "c"], ["d", "e", "f"]])             

    def test_with_tabs(self):
        str_io = StringIO("a\tb\tc\n")
        rows = [row for row in custom_reader(str_io, "\t", -1)]

        self.assertEqual(rows, [["a", "b", "c"]])        

    def test_with_null_field(self):
        str_io = StringIO("a,\\N,c\n")
        rows = [row for row in custom_reader(str_io, ",", -1)]

        self.assertEqual(rows, [["a", "\\N", "c"]])        
    
    def test_with_split_end_column(self):
        str_io = StringIO("a,b,c\nd,e,f,f")
        rows = [row for row in custom_reader(str_io, ",", -1)]

        self.assertEqual(rows, [['a', 'b', 'c'], ['d', 'e', 'f,f']])

    def test_with_split_middle_column(self):
        str_io = StringIO("a,b,c\nd,e,e,f")
        rows = [row for row in custom_reader(str_io, ",", 1)]

        self.assertEqual(rows, [['a', 'b', 'c'], ['d', 'e,e', 'f']])        

    def test_with_multiline_row(self):
        str_io = StringIO(
                            "abk\t4\tbackstreetboys\tunited states\n"
                            "\\\n"
                            "American flag\n"
                            "\\\n"
                            "\n"
        )
        rows = [row for row in custom_reader(str_io, "\t", -1)]

        self.assertEqual(rows, [['abk', 
                                 '4', 
                                 'backstreetboys', 
                                 'united states \\ American flag \\ ']])        


if __name__ == "__main__":
    unittest.main()
