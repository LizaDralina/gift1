from typing import List

from app.models.product import Product
from app.models.recipient import Recipient
from app.schemas.recommendation import RecommendationItem
from app.utils.text import normalize_list, normalize_text
from app.ml.model_loader import load_model
from app.ml.features import build_feature_vector


def product_matches_budget(product: Product, budget_min: float, budget_max: float) -> bool:
    return budget_min <= product.price <= budget_max


def product_matches_age(product: Product, recipient: Recipient) -> bool:
    return product.age_limit <= recipient.age


def product_matches_exclusions(product: Product, recipient: Recipient) -> bool:
    exclusions = set(normalize_list(recipient.exclusions))
    if normalize_text(product.category) in exclusions:
        return False
    if normalize_text(product.name) in exclusions:
        return False
    return True


def product_matches_categories(product: Product, categories: List[str]) -> bool:
    if not categories:
        return True
    categories_norm = set(normalize_list(categories))
    return normalize_text(product.category) in categories_norm


def product_matches_occasion(product: Product, recipient: Recipient) -> bool:
    tags = set(normalize_list(product.occasion_tags))
    if not tags:
        return True
    return normalize_text(recipient.occasion) in tags


def product_matches_relationship(product: Product, recipient: Recipient) -> bool:
    tags = set(normalize_list(product.relationship_tags))
    if not tags:
        return True
    if not recipient.relationship_type:
        return True
    return normalize_text(recipient.relationship_type) in tags


def score_product(
    product: Product,
    recipient: Recipient,
    budget_min: float,
    budget_max: float,
    categories: List[str],
):
    score = 0.0
    reasons = []

    recipient_interests = set(normalize_list(recipient.interests))
    product_interests = set(normalize_list(product.interest_tags))
    category_norm = normalize_text(product.category)

    matches = recipient_interests.intersection(product_interests)
    if category_norm in recipient_interests:
        matches.add(category_norm)

    if matches:
        score += 3.0 * len(matches)
        for match in list(matches)[:2]:
            reasons.append(f"Соответствует интересу «{match}»")

    if budget_max > budget_min:
        budget_fit = (product.price - budget_min) / (budget_max - budget_min)
        budget_fit = max(0.0, min(1.0, budget_fit))
    else:
        budget_fit = 1.0

    score += 2.0 * budget_fit
    reasons.append(f"Попадает в бюджет ({product.price:.0f} руб.)")

    if product_matches_occasion(product, recipient):
        score += 1.5
        reasons.append(f"Подходит для повода «{recipient.occasion}»")

    if recipient.relationship_type and product_matches_relationship(product, recipient):
        score += 1.0
        reasons.append(f"Уместно для типа отношений «{recipient.relationship_type}»")

    if categories and category_norm in set(normalize_list(categories)):
        score += 0.5

    reasons = reasons[:4]
    return round(score, 3), reasons

def generate_recommendations(
    recipient: Recipient,
    products: List[Product],
    budget_min: float,
    budget_max: float,
    categories: List[str],
    top_k: int,
) -> List[RecommendationItem]:
    result = []
    model = load_model()

    for product in products:
        if not product_matches_budget(product, budget_min, budget_max):
            continue
        if not product_matches_age(product, recipient):
            continue
        if not product_matches_exclusions(product, recipient):
            continue
        if not product_matches_categories(product, categories):
            continue
        if not product_matches_occasion(product, recipient):
            continue
        if not product_matches_relationship(product, recipient):
            continue

        heuristic_score, reasons = score_product(
            product=product,
            recipient=recipient,
            budget_min=budget_min,
            budget_max=budget_max,
            categories=categories,
        )


        # if model:
        #     features = build_feature_vector(
        #         product=product,
        #         recipient=recipient,
        #         budget_min=budget_min,
        #         budget_max=budget_max,
        #         categories=categories,
        #     )
        #     ml_score = float(model.predict([features])[0])
        #     final_score = 0.7 * ml_score + 0.3 * heuristic_score
        # else:
        #     final_score = heuristic_score

        if model:
            features = build_feature_vector(
                product=product,
                recipient=recipient,
                budget_min=budget_min,
                budget_max=budget_max,
                categories=categories,
            )
            ml_score = float(model.predict([features])[0])
            print(f"ML score for product {product.id} ({product.name}): {ml_score}, features={features}")
            final_score = 0.7 * ml_score + 0.3 * heuristic_score
        else:
            final_score = heuristic_score

        result.append(
            RecommendationItem(
                product_id=product.id,
                name=product.name,
                description=product.description,
                price=product.price,
                category=product.category,
                brand=product.brand,
                image_url=product.image_url,
                score=round(final_score, 3),
                reasons=reasons,
            )
        )

    result.sort(key=lambda x: x.score, reverse=True)
    return result[:top_k]

# def generate_recommendations(
#     recipient: Recipient,
#     products: List[Product],
#     budget_min: float,
#     budget_max: float,
#     categories: List[str],
#     top_k: int,
# ) -> List[RecommendationItem]:
#     result = []

#     for product in products:
#         if not product_matches_budget(product, budget_min, budget_max):
#             continue
#         if not product_matches_age(product, recipient):
#             continue
#         if not product_matches_exclusions(product, recipient):
#             continue
#         if not product_matches_categories(product, categories):
#             continue
#         if not product_matches_occasion(product, recipient):
#             continue
#         if not product_matches_relationship(product, recipient):
#             continue

#         score, reasons = score_product(
#             product=product,
#             recipient=recipient,
#             budget_min=budget_min,
#             budget_max=budget_max,
#             categories=categories,
#         )

#         result.append(
#             RecommendationItem(
#                 product_id=product.id,
#                 name=product.name,
#                 description=product.description,
#                 price=product.price,
#                 category=product.category,
#                 brand=product.brand,
#                 image_url=product.image_url,
#                 score=score,
#                 reasons=reasons,
#             )
#         )

#     result.sort(key=lambda x: x.score, reverse=True)
#     return result[:top_k]