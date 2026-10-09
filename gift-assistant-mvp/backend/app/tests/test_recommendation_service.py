from types import SimpleNamespace
from app.services.recommendation_service import generate_recommendations, score_product

def make_product(
    id,
    name,
    price,
    category,
    age_limit=0,
    interest_tags=None,
    occasion_tags=None,
    relationship_tags=None,
    description="Описание",
    brand="TestBrand",
    image_url=None,):
    return SimpleNamespace(
        id=id,
        name=name,
        description=description,
        price=price,
        category=category,
        brand=brand,
        age_limit=age_limit,
        image_url=image_url,
        interest_tags=interest_tags or [],
        occasion_tags=occasion_tags or [],
        relationship_tags=relationship_tags or [],
    )

def make_recipient():
    return SimpleNamespace(
        age=23,
        gender="female",
        relationship_type="друг",
        occasion="день рождения",
        interests=["космос", "книги", "техника"],
        exclusions=["дом"],
    )

def test_score_product_has_reasons():
    product = make_product(
        id=1,
        name="Книга по астрономии",
        price=1200,
        category="книги",
        age_limit=12,
        interest_tags=["космос", "книги"],
        occasion_tags=["день рождения"],
        relationship_tags=["друг"],
    )
    recipient = make_recipient()

    score, reasons = score_product(
        product=product,
        recipient=recipient,
        budget_min=1000,
        budget_max=5000,
        categories=["книги"],
    )

    assert score > 0
    assert len(reasons) > 0
    assert any("бюджет" in reason.lower() for reason in reasons)

def test_generate_recommendations_filters_invalid_products():
    recipient = make_recipient()

    products = [
        make_product(
            id=1,
            name="Книга по астрономии",
            price=1200,
            category="книги",
            age_limit=12,
            interest_tags=["космос", "книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=2,
            name="Очень дорогой телескоп",
            price=50000,
            category="техника",
            age_limit=12,
            interest_tags=["космос"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=3,
            name="Плед",
            price=1800,
            category="дом",
            age_limit=0,
            interest_tags=["уют"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=4,
            name="Товар 18+",
            price=2000,
            category="книги",
            age_limit=30,
            interest_tags=["книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
    ]

    recommendations = generate_recommendations(
        recipient=recipient,
        products=products,
        budget_min=1000,
        budget_max=5000,
        categories=["книги", "техника"],
        top_k=10,
    )

    names = [item.name for item in recommendations]

    assert "Книга по астрономии" in names
    assert "Очень дорогой телескоп" not in names
    assert "Плед" not in names
    assert "Товар 18+" not in names

def test_generate_recommendations_returns_top_k():
    recipient = make_recipient()

    products = [
        make_product(
            id=i,
            name=f"Книга {i}",
            price=1000 + i * 100,
            category="книги",
            age_limit=0,
            interest_tags=["книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        )
        for i in range(1, 10)
    ]

    recommendations = generate_recommendations(
        recipient=recipient,
        products=products,
        budget_min=1000,
        budget_max=5000,
        categories=["книги"],
        top_k=5,
    )

    assert len(recommendations) == 5

def test_generate_recommendations_all_have_reasons():
    recipient = make_recipient()

    products = [
        make_product(
            id=1,
            name="Книга по астрономии",
            price=1200,
            category="книги",
            age_limit=12,
            interest_tags=["космос", "книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=2,
            name="Портативная колонка",
            price=3400,
            category="техника",
            age_limit=0,
            interest_tags=["техника"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
    ]

    recommendations = generate_recommendations(
        recipient=recipient,
        products=products,
        budget_min=1000,
        budget_max=5000,
        categories=["книги", "техника"],
        top_k=10,
    )

    assert len(recommendations) > 0
    assert all(len(item.reasons) > 0 for item in recommendations)

def test_generate_recommendations_respects_budget():
    recipient = make_recipient()

    products = [
        make_product(
            id=1,
            name="Подходящий подарок",
            price=2000,
            category="книги",
            interest_tags=["книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=2,
            name="Слишком дешёвый подарок",
            price=100,
            category="книги",
            interest_tags=["книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
        make_product(
            id=3,
            name="Слишком дорогой подарок",
            price=10000,
            category="книги",
            interest_tags=["книги"],
            occasion_tags=["день рождения"],
            relationship_tags=["друг"],
        ),
    ]

    recommendations = generate_recommendations(
        recipient=recipient,
        products=products,
        budget_min=1000,
        budget_max=5000,
        categories=["книги"],
        top_k=10,
    )

    assert all(1000 <= item.price <= 5000 for item in recommendations)
