import random
from dataclasses import dataclass
from typing import List, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score


RANDOM_STATE = 42


FEATURE_COLUMNS = [
    "interest_matches",
    "price",
    "price_position",
    "occasion_match",
    "relationship_match",
    "category_match",
    "recipient_age",
    "product_age_limit",
    "heuristic_score",
]


@dataclass
class EvaluationResult:
    approach: str
    ndcg_5: float
    ndcg_10: float
    map_5: float
    map_10: float


def build_dataset() -> pd.DataFrame:
    """
    Формирует экспертно размеченный датасет для MVP.

    Каждая строка — это пара "профиль получателя — товар".
    target_score — экспертная оценка релевантности от 0 до 1.
    heuristic_score — score, рассчитанный по интерпретируемым правилам.
    """

    rows = [
        # Хорошие совпадения: космос, книги, техника
        [2, 1200, 0.05, 1, 1, 1, 23, 12, 0.90, 0.95],
        [1, 2700, 0.42, 1, 1, 1, 23, 6, 0.78, 0.85],
        [1, 3400, 0.60, 1, 1, 1, 23, 0, 0.72, 0.75],
        [1, 4800, 0.95, 1, 1, 1, 23, 0, 0.74, 0.80],
        [2, 1400, 0.10, 1, 1, 0, 23, 12, 0.70, 0.82],
        [1, 2600, 0.40, 1, 1, 0, 23, 0, 0.68, 0.78],

        # Частично релевантные
        [1, 1800, 0.20, 1, 0, 1, 23, 0, 0.55, 0.55],
        [1, 2300, 0.32, 0, 1, 1, 23, 0, 0.50, 0.48],
        [0, 1500, 0.15, 1, 1, 0, 23, 0, 0.45, 0.42],
        [0, 2200, 0.30, 1, 1, 1, 23, 12, 0.48, 0.50],
        [1, 3000, 0.50, 0, 1, 0, 23, 0, 0.46, 0.45],
        [1, 4100, 0.78, 1, 0, 1, 23, 0, 0.57, 0.58],

        # Низкая релевантность
        [0, 900, 0.00, 0, 0, 0, 23, 0, 0.15, 0.10],
        [0, 9000, 1.00, 0, 0, 0, 23, 12, 0.10, 0.05],
        [0, 1800, 0.20, 0, 0, 0, 23, 0, 0.18, 0.15],
        [0, 5200, 1.00, 0, 0, 1, 23, 0, 0.22, 0.18],
        [0, 700, 0.00, 0, 1, 0, 23, 0, 0.25, 0.20],
        [0, 10000, 1.00, 1, 0, 0, 23, 18, 0.12, 0.08],

        # Спорт-профиль
        [2, 2500, 0.45, 1, 1, 1, 28, 0, 0.86, 0.90],
        [1, 1300, 0.10, 1, 1, 1, 28, 0, 0.74, 0.78],
        [1, 1700, 0.20, 1, 1, 1, 28, 0, 0.76, 0.80],
        [0, 3400, 0.60, 0, 1, 0, 28, 0, 0.35, 0.30],
        [0, 1200, 0.08, 1, 0, 0, 28, 12, 0.30, 0.25],

        # Коллега / офис
        [2, 1300, 0.12, 1, 1, 1, 35, 0, 0.82, 0.88],
        [1, 900, 0.00, 1, 1, 1, 35, 0, 0.70, 0.74],
        [1, 1100, 0.05, 1, 1, 1, 35, 0, 0.71, 0.76],
        [0, 3200, 0.55, 1, 0, 0, 35, 0, 0.28, 0.22],
        [0, 4800, 0.95, 0, 0, 1, 35, 0, 0.34, 0.30],

        # Дом / уют
        [2, 1800, 0.20, 1, 1, 1, 45, 0, 0.85, 0.90],
        [1, 1700, 0.18, 1, 1, 1, 45, 0, 0.80, 0.84],
        [1, 2600, 0.40, 1, 1, 1, 45, 0, 0.76, 0.80],
        [0, 6200, 1.00, 0, 0, 1, 45, 0, 0.20, 0.16],
        [0, 700, 0.00, 1, 0, 0, 45, 0, 0.26, 0.22],
    ]

    columns = FEATURE_COLUMNS + ["target_score"]
    return pd.DataFrame(rows, columns=columns)


def binarize_relevance(scores: List[float], threshold: float = 0.7) -> List[int]:
    """
    Для MAP@K считаем товар релевантным, если target_score >= threshold.
    """
    return [1 if score >= threshold else 0 for score in scores]


def average_precision_at_k(relevance: List[int], k: int) -> float:
    """
    AP@K для одного списка рекомендаций.
    relevance — список 0/1 в порядке выдачи.
    """
    relevance = relevance[:k]

    if not relevance:
        return 0.0

    num_relevant = 0
    precision_sum = 0.0

    for i, rel in enumerate(relevance, start=1):
        if rel == 1:
            num_relevant += 1
            precision_sum += num_relevant / i

    if num_relevant == 0:
        return 0.0

    return precision_sum / min(num_relevant, k)


def map_at_k(grouped_relevance: List[List[int]], k: int) -> float:
    """
    MAP@K по нескольким группам/запросам.
    """
    if not grouped_relevance:
        return 0.0

    return float(
        np.mean([average_precision_at_k(rel_list, k) for rel_list in grouped_relevance])
    )

def evaluate_order(
    df: pd.DataFrame,
    score_column: str,
    k_values=(5, 10),
) -> Dict[str, float]:
    """
    Оценивает порядок товаров по заданной колонке score_column.
    В упрощённой MVP-версии весь test-set рассматривается как один список выдачи.
    """

    ordered = df.sort_values(score_column, ascending=False)

    y_true = ordered["target_score"].to_numpy().reshape(1, -1)
    y_score = ordered[score_column].to_numpy().reshape(1, -1)

    result = {}

    for k in k_values:
        k_eff = min(k, len(ordered))

        result[f"ndcg_{k}"] = float(ndcg_score(y_true, y_score, k=k_eff))

        relevance_binary = binarize_relevance(ordered["target_score"].tolist())
        result[f"map_{k}"] = average_precision_at_k(relevance_binary, k_eff)

    return result


def evaluate_random_baseline(test_df: pd.DataFrame) -> EvaluationResult:
    random_df = test_df.copy()

    rng = random.Random(RANDOM_STATE)
    random_scores = [rng.random() for _ in range(len(random_df))]
    random_df["random_score"] = random_scores

    metrics = evaluate_order(random_df, "random_score")

    return EvaluationResult(
        approach="Random baseline",
        ndcg_5=metrics["ndcg_5"],
        ndcg_10=metrics["ndcg_10"],
        map_5=metrics["map_5"],
        map_10=metrics["map_10"],
    )


def evaluate_heuristic_baseline(test_df: pd.DataFrame) -> EvaluationResult:
    heuristic_df = test_df.copy()
    metrics = evaluate_order(heuristic_df, "heuristic_score")

    return EvaluationResult(
        approach="Heuristic-only",
        ndcg_5=metrics["ndcg_5"],
        ndcg_10=metrics["ndcg_10"],
        map_5=metrics["map_5"],
        map_10=metrics["map_10"],
    )


def evaluate_hybrid_model(train_df: pd.DataFrame, test_df: pd.DataFrame) -> EvaluationResult:
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df["target_score"]

    X_test = test_df[FEATURE_COLUMNS]

    model = GradientBoostingRegressor(random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    hybrid_df = test_df.copy()
    hybrid_df["ml_score"] = model.predict(X_test)

    # Нормализуем heuristic_score в диапазон [0, 1],
    # так как target_score и ml_score находятся примерно в этом диапазоне.
    heuristic = hybrid_df["heuristic_score"].clip(0, 1)
    ml_score = hybrid_df["ml_score"].clip(0, 1)

    hybrid_df["hybrid_score"] = 0.7 * heuristic + 0.3 * ml_score

    metrics = evaluate_order(hybrid_df, "hybrid_score")

    return EvaluationResult(
        approach="Hybrid heuristic+ML",
        ndcg_5=metrics["ndcg_5"],
        ndcg_10=metrics["ndcg_10"],
        map_5=metrics["map_5"],
        map_10=metrics["map_10"],
    )


def print_results(results: List[EvaluationResult], dataset_size: int, test_size: int):
    print("\nModel validation results")
    print("=" * 72)
    print(f"Dataset size: {dataset_size} samples")
    print(f"Train/test split: 80/20")
    print(f"Test size: {test_size} samples")
    print("-" * 72)
    print(f"{'Approach':<24} {'NDCG@5':>10} {'NDCG@10':>10} {'MAP@5':>10} {'MAP@10':>10}")
    print("-" * 72)

    for r in results:
        print(
            f"{r.approach:<24} "
            f"{r.ndcg_5:>10.3f} "
            f"{r.ndcg_10:>10.3f} "
            f"{r.map_5:>10.3f} "
            f"{r.map_10:>10.3f}"
        )

    print("=" * 72)
    print(
        "Interpretation: higher NDCG/MAP indicates better ordering of relevant gifts "
        "in the top of the recommendation list."
    )
    print()


def main():
    df = build_dataset()

    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=RANDOM_STATE,
        shuffle=True,
    )

    results = [
        evaluate_random_baseline(test_df),
        evaluate_heuristic_baseline(test_df),
        evaluate_hybrid_model(train_df, test_df),
    ]

    print_results(
        results=results,
        dataset_size=len(df),
        test_size=len(test_df),
    )


if __name__ == "__main__":
    main()