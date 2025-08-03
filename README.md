# CANLogParser

A simple parser that converts Vector `.asc` CAN log files into a pandas
`DataFrame`.

## Usage

```bash
python asc_parser.py path/to/log.asc
```

From Python you can use the ``ASCParser`` class:

```python
from asc_parser import ASCParser

parser = ASCParser()
df = parser.parse_file("path/to/log.asc")
```

A convenience ``asc_to_dataframe`` function is also provided for one-off
conversions.
