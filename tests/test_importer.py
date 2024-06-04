import csv
from io import BytesIO, StringIO, TextIOWrapper
import os
from discovery import importer
from rscbulkenrollment.rsc import rsc as rscpkg

def test_guess_dialect():
    # Test case 1: TextIOWrapper object
    csv_object = StringIO("a,b,c\n1,2,3\n")
    dialect = importer.guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 2: List object
    csv_object = [['a', 'b', 'c'], ['1', '2', '3']]
    dialect = importer.guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 3: Empty csv_object
    csv_object = []
    dialect = importer.guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ','
    assert dialect.quotechar == '"'
    assert dialect.escapechar is None
    assert dialect.doublequote is True
    assert dialect.lineterminator == '\r\n'
    assert dialect.quoting == csv.QUOTE_MINIMAL

    # Test case 4: TextIOWrapper object with semicolons as separators
    csv_object = TextIOWrapper(BytesIO(b"a;b;c\n1;2;3\n"))
    dialect = importer.guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == ';'

    # Test case 5: TextIOWrapper object with tabs as separators
    csv_object = TextIOWrapper(BytesIO(b"a\tb\tc\n1\t2\t3\n"))
    dialect = importer.guess_dialect(csv_object)
    assert issubclass(dialect, csv.Dialect)
    assert dialect.delimiter == '\t'

def test_file_types():

    rsc1 = rscpkg.RSC('192.168.0.67','123456789abcdef0!', "")
    rsc2 = rscpkg.RSC('192.168.0.17','123456789abcdef0+', "")

    for filename in os.listdir('tests/resources'):
        result = importer.import_rscs(filename=f'tests/resources/{filename}')
        assert isinstance(result, list)
        assert all(isinstance(rsc, rscpkg.RSC) for rsc in result)
        # Verify that the RSCs are the same as the ones in the file
        assert rsc1 in result
        assert rsc2 in result

