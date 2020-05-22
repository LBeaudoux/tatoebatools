from io import StringIO
from tatoebatools.datafile import (
    custom_reader,
    get_mapped_fields,
    unsplit_field,
)


def test_unsplit_field_without_split_field():
    row = ["foobar", "text not split by delimiters"]
    unsplit_row = unsplit_field(row, nb_cols=2, delimiter=",", index_field=-1)
    assert unsplit_row == row


def test_unsplit_field_with_end_split_field():
    nok_row = ["foobar", "text", " split", " by", " delimiters"]
    ok_row = ["foobar", "text, split, by, delimiters"]
    unsplit_row = unsplit_field(
        nok_row, nb_cols=2, delimiter=",", index_field=-1
    )
    assert unsplit_row == ok_row


def test_unsplit_field_with_midlle_split_field():
    nok_row = ["foobar", "text", " split", " by", " delimiters", "foo"]
    ok_row = ["foobar", "text, split, by, delimiters", "foo"]
    unsplit_row = unsplit_field(
        nok_row, nb_cols=3, delimiter=",", index_field=1
    )
    assert unsplit_row == ok_row


def test_custom_reader_with_commas():
    str_io = StringIO("a,b,c\n")
    rows = [row for row in custom_reader(str_io, ",", -1)]
    assert rows == [["a", "b", "c"]]


def test_custom_reader_with_multiple_rows():
    str_io = StringIO("a,b,c\nd,e,f\n")
    rows = [row for row in custom_reader(str_io, ",", -1)]
    assert rows == [["a", "b", "c"], ["d", "e", "f"]]


def test_custom_reader_with_tabs():
    str_io = StringIO("a\tb\tc\n")
    rows = [row for row in custom_reader(str_io, "\t", -1)]
    assert rows == [["a", "b", "c"]]


def test_custom_reader_with_null_field():
    str_io = StringIO("a,\\N,c\n")
    rows = [row for row in custom_reader(str_io, ",", -1)]
    assert rows == [["a", "\\N", "c"]]


def test_custom_reader_with_split_end_column():
    str_io = StringIO("a,b,c\nd,e,f,f")
    rows = [row for row in custom_reader(str_io, ",", -1)]
    assert rows == [["a", "b", "c"], ["d", "e", "f,f"]]


def test_custom_reader_with_split_middle_column():
    str_io = StringIO("a,b,c\nd,e,e,f")
    rows = [row for row in custom_reader(str_io, ",", 1)]
    assert rows == [["a", "b", "c"], ["d", "e,e", "f"]]


def test_custom_reader_with_multiline_row():
    str_io = StringIO(
        "abk\t4\tbackstreetboys\tunited states\n"
        "\\\n"
        "American flag\n"
        "\\\n"
        "\n"
    )
    rows = [row for row in custom_reader(str_io, "\t", -1)]
    assert rows == [
        ["abk", "4", "backstreetboys", "united states \\ American flag \\ "]
    ]


def test_get_mapped_fields_without_index():
    row = ["foo", "bar"]
    columns = [1]
    index = {}
    int_key = False
    assert get_mapped_fields(row, columns, index, int_key) == ["bar"]


def test_get_mapped_fields_with_too_short_row():
    row = ["foo", "bar"]
    columns = [2]
    index = {}
    int_key = False
    assert get_mapped_fields(row, columns, index, int_key) == [""]


def test_get_mapped_fields_with_index():
    row = ["23", "42"]
    index = {"23": "foo", "42": "bar"}
    columns = [0, 1]
    int_key = False
    assert get_mapped_fields(row, columns, index, int_key) == ["foo", "bar"]


def test_get_mapped_fields_with_int_index():
    row = ["23", "42"]
    index = {23: "foo", 42: "bar"}
    columns = [0, 1]
    int_key = True
    assert get_mapped_fields(row, columns, index, int_key) == ["foo", "bar"]
