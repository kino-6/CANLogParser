"""Parser for Vector ASC CAN log files."""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


class ASCParser:
    """Parse Vector ``.asc`` CAN log files."""

    def parse_line(self, line: str) -> Optional[Dict[str, object]]:
        """Parse a single line from an ASC file.

        Comment lines and malformed lines return ``None``.
        """

        line = line.strip()
        if not line or line.startswith((";", "/", "(", "[")):
            return None

        parts = line.split()
        if len(parts) < 5:
            return None

        try:
            timestamp = float(parts[0])
            channel = int(parts[1])
            can_id = int(parts[2], 16) if parts[2].startswith("0x") else int(parts[2])
            dlc = int(parts[3])
            data_bytes = [int(b, 16) for b in parts[4 : 4 + dlc]]
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
        """Parse an ASC file at ``path`` into a :class:`pandas.DataFrame`."""

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

