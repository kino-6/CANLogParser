"""Parser for Vector ASC CAN log files."""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


class ASCParser:
    """Parser for Vector ``.asc`` CAN log files.

    The class exposes two public methods:

    ``parse_line``
        Translate a single line of text into a dictionary containing
        ``timestamp``, ``channel``, ``can_id``, ``dlc`` and ``data`` fields.
        Lines that are comments, error frames or otherwise malformed are
        skipped by returning ``None``.  Optional direction (``Rx``/``Tx``)
        and frame type (``d``/``r``) tokens are tolerated and ignored, and
        any extra tokens following the payload are discarded.

    ``parse_file``
        Iterate over all lines of a log file and return a
        :class:`pandas.DataFrame` containing only successfully parsed frames.
    """

    def parse_line(self, line: str) -> Optional[Dict[str, object]]:
        """Parse a single line from an ASC file.

        Parameters
        ----------
        line:
            Raw line from the ``.asc`` log.

        Returns
        -------
        dict | None
            Mapping with CAN frame attributes if the line is valid, otherwise
            ``None`` when the line is a comment, an error frame or has
            insufficient/malformed data.
        """

        line = line.strip()
        if not line or line.startswith((";", "/", "(", "[")):
            return None

        parts = line.split()

        if "ErrorFrame" in parts or len(parts) < 4:
            return None

        try:
            timestamp = float(parts[0])
            channel = int(parts[1])
            can_id = int(parts[2], 16) if parts[2].startswith("0x") else int(parts[2])

            idx = 3
            if len(parts) > idx and parts[idx] in {"Rx", "Tx"}:
                idx += 1
            if len(parts) > idx and parts[idx] in {"d", "r"}:
                idx += 1
            if len(parts) <= idx:
                return None
            dlc = int(parts[idx])
            data_start = idx + 1
            if len(parts) < data_start + dlc:
                return None
            data_bytes = [int(b, 16) for b in parts[data_start : data_start + dlc]]
        except ValueError:
            return None

        return {
            "timestamp": timestamp,
            "channel": channel,
            "can_id": can_id,
            "dlc": dlc,
            "data": data_bytes,
        }

    def parse_file(self, path: str) -> pd.DataFrame:
        """Parse an ASC file into a :class:`pandas.DataFrame`.

        Each line is fed through :meth:`parse_line`; only successful parses
        are included in the resulting frame.  The columns of the returned
        frame match the keys produced by ``parse_line``.
        """

        records: List[Dict[str, object]] = []
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                record = self.parse_line(line)
                if record is not None:
                    records.append(record)
        return pd.DataFrame(records)


def asc_to_dataframe(path: str) -> pd.DataFrame:
    """Backward-compatible helper to parse an ASC file into a DataFrame."""

    return ASCParser().parse_file(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse an ASC file and output a DataFrame"
    )
    parser.add_argument("path", help="Path to the .asc log file")
    args = parser.parse_args()

    df = asc_to_dataframe(args.path)
    print(df)

