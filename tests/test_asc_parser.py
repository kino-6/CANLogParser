import pathlib
import sys

import pandas as pd

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from asc_parser import ASCParser, asc_to_dataframe


def test_parse_line_valid():
    parser = ASCParser()
    line = "0.000000 1 0x123 8 11 22 33 44 55 66 77 88"
    record = parser.parse_line(line)
    assert record == {
        "timestamp": 0.0,
        "channel": 1,
        "can_id": 0x123,
        "dlc": 8,
        "data": [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
    }


def test_parse_line_comment():
    parser = ASCParser()
    assert parser.parse_line("; comment") is None


def test_parse_file():
    parser = ASCParser()
    df = parser.parse_file("tests/sample.asc")

    assert list(df["timestamp"]) == [0.0, 0.1]
    assert df["channel"].tolist() == [1, 1]
    assert df["can_id"].tolist() == [0x123, 0x123]
    assert df["dlc"].tolist() == [8, 8]
    assert df["data"].tolist() == [
        [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
        [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80],
    ]


def test_asc_to_dataframe_wrapper():
    df = asc_to_dataframe("tests/sample.asc")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2

