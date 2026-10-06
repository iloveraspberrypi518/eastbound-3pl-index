"""Minimal .xlsx reader using only the standard library (no openpyxl needed)."""
import re
import xml.etree.ElementTree as ET
import zipfile

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_rows(path, sheet=0):
    """Yield each row of a worksheet as a list of cell values (str, float or None)."""
    z = zipfile.ZipFile(path)
    strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])) for si in root.findall("m:si", NS)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels}
    sheets = wb.find("m:sheets", NS)
    rid = sheets[sheet].get("{%s}id" % NS["r"]) if isinstance(sheet, int) else \
        next(s for s in sheets if s.get("name") == sheet).get("{%s}id" % NS["r"])
    ws = ET.fromstring(z.read("xl/" + target[rid].lstrip("/").removeprefix("xl/")))
    for row in ws.iter("{%s}row" % NS["m"]):
        out = []
        for c in row.findall("m:c", NS):
            i = _col(c.get("r"))
            out += [None] * (i - len(out))
            v = c.find("m:v", NS)
            if c.get("t") == "s" and v is not None:
                val = strings[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
            elif v is not None:
                try:
                    val = float(v.text)
                except ValueError:
                    val = v.text
            else:
                val = None
            out.append(val)
        yield out
