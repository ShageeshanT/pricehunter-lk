from pricehunter.engine import ResearchEngine
from pricehunter.models import ResearchItem


def test_engine_recommends_candidate_and_total():
    report = ResearchEngine().research([ResearchItem(name="A4 file", quantity=100)])
    recommendation = report.items[0]
    assert recommendation.recommended is not None
    assert recommendation.recommended.vendor == "OfficeMart LK"
    assert recommendation.estimated_total == 9500
    assert report.grand_total == 9500


def test_engine_warns_for_missing_candidate():
    report = ResearchEngine().research([ResearchItem(name="quantum banana cannon", quantity=2)])
    assert report.items[0].recommended is None
    assert "No price candidates found." in report.items[0].warnings
