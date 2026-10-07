from notifications.lookups import ItemCatalog, ItemInfo, PlayerDirectory, Rarity

SWORD = ItemInfo("Sword of Azeroth", Rarity.LEGENDARY)


def test_known_player_display_name():
    assert PlayerDirectory({3: "Cyra"}).display_name(3) == "Cyra"


def test_unknown_player_falls_back_to_id():
    assert PlayerDirectory({3: "Cyra"}).display_name(7) == "7"


def test_known_item_lookup():
    assert ItemCatalog({"SwordOfAzeroth": SWORD}).lookup("SwordOfAzeroth") == SWORD


def test_unknown_item_returns_none():
    assert ItemCatalog({"SwordOfAzeroth": SWORD}).lookup("BananaPeel") is None


def test_item_lookup_is_case_sensitive():
    assert ItemCatalog({"SwordOfAzeroth": SWORD}).lookup("swordofazeroth") is None


def test_rarity_order_and_label():
    assert Rarity.COMMON < Rarity.RARE < Rarity.LEGENDARY
    assert Rarity.LEGENDARY.label == "legendary"
