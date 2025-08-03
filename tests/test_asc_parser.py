"""Unit tests for the ASC log parser.

The tests are organised by feature to make the expected behaviour explicit
and to ease future expansion.  Shared fixtures provide reusable parser
instances and common file paths.
"""

import pathlib
import sys

import pandas as pd
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from asc_parser import ASCParser, asc_to_dataframe


@pytest.fixture
def parser() -> ASCParser:
    """Return a fresh :class:`ASCParser` for each test."""

    return ASCParser()


@pytest.fixture
def sample_path() -> str:
    """Path to the bundled sample ``.asc`` log file."""

    return "tests/sample.asc"


class TestParseLine:
    """Line-level parsing scenarios for :meth:`ASCParser.parse_line`."""

    def test_valid_line(self, parser: ASCParser) -> None:
        """A well-formed line is converted into a dictionary."""

        line = "0.000000 1 0x123 8 11 22 33 44 55 66 77 88"
        record = parser.parse_line(line)
        assert record == {
            "timestamp": 0.0,
            "channel": 1,
            "can_id": 0x123,
            "dlc": 8,
            "data": [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
        }

    def test_comment_line(self, parser: ASCParser) -> None:
        """Lines starting with ';' are treated as comments and ignored."""

        assert parser.parse_line("; comment") is None

    def test_direction_and_extra(self, parser: ASCParser) -> None:
        """Optional direction/type tokens and trailing text are ignored."""

        line = "0.200000 1 0x321 Rx d 2 01 02 junk"
        record = parser.parse_line(line)
        assert record == {
            "timestamp": 0.2,
            "channel": 1,
            "can_id": 0x321,
            "dlc": 2,
            "data": [0x01, 0x02],
        }

    def test_error_and_malformed(self, parser: ASCParser) -> None:
        """Error frames and truncated payloads return ``None``."""

        assert parser.parse_line("0.050000 1 ErrorFrame") is None
        assert parser.parse_line("0.300000 1 0x100 4 01 02") is None


class TestFileConversion:
    """Integration tests for file-level parsing helpers."""

    def test_parse_file(self, parser: ASCParser, sample_path: str) -> None:
        """``parse_file`` aggregates valid frames into a DataFrame."""

        df = parser.parse_file(sample_path)
        assert list(df["timestamp"]) == [0.0, 0.1, 0.2]
        assert df["channel"].tolist() == [1, 1, 1]
        assert df["can_id"].tolist() == [0x123, 0x123, 0x321]
        assert df["dlc"].tolist() == [8, 8, 2]
        assert df["data"].tolist() == [
            [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
            [0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80],
            [0x01, 0x02],
        ]

    def test_asc_to_dataframe_wrapper(self, sample_path: str) -> None:
        """The convenience wrapper returns a populated DataFrame."""

        df = asc_to_dataframe(sample_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

