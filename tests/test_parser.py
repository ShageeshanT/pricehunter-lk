from pricehunter.parser import parse_item_line, parse_items_text


def test_parse_item_line_with_comma_quantity():
    item = parse_item_line("A4 file, 100")
    assert item is not None
    assert item.name == "A4 file"
    assert item.quantity == 100


def test_parse_item_line_with_x_quantity():
    item = parse_item_line("Blue pen x 25")
    assert item is not None
    assert item.name == "Blue pen"
    assert item.quantity == 25


def test_parse_items_text_skips_comments():
    items = parse_items_text("# budget\nPlaque, 10\n\nSticker sheet, 50")
    assert [item.name for item in items] == ["Plaque", "Sticker sheet"]
