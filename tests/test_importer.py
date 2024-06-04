import csv
from io import BytesIO, StringIO, TextIOWrapper
from discovery.importer import guess_dialect

def test_guess_dialect():
    # Test case 1: TextIOWrapper object
    csv_object = StringIO("a,b,c\n1,2,3\n")
    dialect = guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 2: List object
    csv_object = [['a', 'b', 'c'], ['1', '2', '3']]
    dialect = guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 3: Empty csv_object
    csv_object = []
    dialect = guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 4: TextIOWrapper object with semicolons as separators
    csv_object = TextIOWrapper(BytesIO(b"a;b;c\n1;2;3\n"))
    dialect = guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ';'

    # Test case 5: TextIOWrapper object with tabs as separators
    csv_object = TextIOWrapper(BytesIO(b"a\tb\tc\n1\t2\t3\n"))
    dialect = guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == '\t'

test_guess_dialect()
