from pricehunter.ranges import PriceRangeFinder


def test_price_range_returns_cheapest_and_most_expensive():
    result = PriceRangeFinder().find_range("A4 file")
    assert result.cheapest is not None
    assert result.most_expensive is not None
    assert result.cheapest.price <= result.most_expensive.price
    assert result.cheapest.site_name
    assert result.most_expensive.site_name


def test_price_range_warns_when_missing():
    result = PriceRangeFinder().find_range("space dragon fuel")
    assert result.cheapest is None
    assert result.most_expensive is None
    assert result.warnings
