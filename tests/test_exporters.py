from pricehunter.engine import ResearchEngine
from pricehunter.exporters import sheets_rows
from pricehunter.models import ResearchItem


def test_sheets_rows_contains_header_and_total():
    report = ResearchEngine().research([ResearchItem(name="Blue pen", quantity=10)])
    rows = sheets_rows(report)
    assert rows[0][0] == "Item"
    assert rows[1][0] == "Blue pen"
    assert rows[-1][0] == "Grand total"
