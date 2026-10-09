from types import SimpleNamespace
from app.services.recommendation_service import (
    product_matches_budget,
    product_matches_age,
    product_matches_exclusions,
    product_matches_categories,
    product_matches_occasion,
    product_matches_relationship,
)

def make_product(
    name="Книга по астрономии",
    price=1200,
    category="книги",
    age_limit=12,
    occasion_tags=None,
    relationship_tags=None,):
    return SimpleNamespace(
        name=name,
        price=price,
        category=category,
        age_limit=age_limit,
        occasion_tags=occasion_tags or [],
        relationship_tags=relationship_tags or [],
    )

def make_recipient(
    age=23,
    occasion="день рождения",
    relationship_type="друг",
    exclusions=None,):
    return SimpleNamespace(
        age=age,
        occasion=occasion,
        relationship_type=relationship_type,
        exclusions=exclusions or [],
    )

def test_product_matches_budget_true():
    product = make_product(price=1500)
    assert product_matches_budget(product, 1000, 2000) is True

def test_product_matches_budget_false():
    product = make_product(price=3000)
    assert product_matches_budget(product, 1000, 2000) is False

def test_product_matches_age_true():
    product = make_product(age_limit=12)
    recipient = make_recipient(age=18)
    assert product_matches_age(product, recipient) is True

def test_product_matches_age_false():
    product = make_product(age_limit=18)
    recipient = make_recipient(age=12)
    assert product_matches_age(product, recipient) is False

def test_product_matches_exclusions_by_category_false():
    product = make_product(category="дом")
    recipient = make_recipient(exclusions=["дом"])
    assert product_matches_exclusions(product, recipient) is False

def test_product_matches_exclusions_true():
    product = make_product(category="книги")
    recipient = make_recipient(exclusions=["дом"])
    assert product_matches_exclusions(product, recipient) is True

def test_product_matches_categories_true():
    product = make_product(category="книги")
    assert product_matches_categories(product, ["книги", "техника"]) is True

def test_product_matches_categories_false():
    product = make_product(category="еда")
    assert product_matches_categories(product, ["книги", "техника"]) is False

def test_product_matches_occasion_true():
    product = make_product(occasion_tags=["день рождения", "новый год"])
    recipient = make_recipient(occasion="день рождения")
    assert product_matches_occasion(product, recipient) is True

def test_product_matches_occasion_false():
    product = make_product(occasion_tags=["новый год"])
    recipient = make_recipient(occasion="день рождения")
    assert product_matches_occasion(product, recipient) is False

def test_product_matches_relationship_true():
    product = make_product(relationship_tags=["друг", "коллега"])
    recipient = make_recipient(relationship_type="друг")
    assert product_matches_relationship(product, recipient) is True

def test_product_matches_relationship_false():
    product = make_product(relationship_tags=["коллега"])
    recipient = make_recipient(relationship_type="партнёр")
    assert product_matches_relationship(product, recipient) is False
