from app.utils.text import normalize_list, normalize_text


def build_feature_vector(product, recipient, budget_min, budget_max, categories):
    recipient_interests = set(normalize_list(recipient.interests))
    product_interests = set(normalize_list(product.interest_tags))
    selected_categories = set(normalize_list(categories))

    interest_matches = len(recipient_interests.intersection(product_interests))
    category_match = int(normalize_text(product.category) in selected_categories)

    if budget_max > budget_min:
        price_position = (product.price - budget_min) / (budget_max - budget_min)
    else:
        price_position = 1.0

    price_position = max(0.0, min(1.0, price_position))

    occasion_match = int(
        normalize_text(recipient.occasion) in normalize_list(product.occasion_tags)
    )

    if recipient.relationship_type:
        relationship_match = int(
            normalize_text(recipient.relationship_type) in normalize_list(product.relationship_tags)
        )
    else:
        relationship_match = 1

    return [
        interest_matches,
        product.price,
        price_position,
        occasion_match,
        relationship_match,
        category_match,
        recipient.age,
        product.age_limit,
    ]