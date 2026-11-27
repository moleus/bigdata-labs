"""Practice 5: streaming Bayesian estimates and optional text classification."""

import argparse
from collections.abc import Iterator

import numpy as np
from numpy.typing import NDArray

CATEGORIES = ("INFO", "WARN", "ERROR", "CRITICAL", "FATAL")
NORMAL = (0.60, 0.25, 0.10, 0.04, 0.01)
DRIFT = (0.20, 0.20, 0.30, 0.20, 0.10)
CHUNK_SIZE = 100
STEPS = 50
DRIFT_STEP = 30  # zero-based: the first shifted batch is displayed as 31
SEED = 42
DECAY = 0.90


def update(
    prior: NDArray[np.float64],
    posterior: NDArray[np.float64],
    counts: NDArray[np.int64],
    decay: float = 1.0,
) -> NDArray[np.float64]:
    return prior + decay * (posterior - prior) + counts


def moments(alpha: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    total = alpha.sum()
    mean = alpha / total
    return mean, np.sqrt(mean * (1.0 - mean) / (total + 1.0))


def dirichlet_demo() -> None:
    rng = np.random.default_rng(SEED)
    prior = np.ones(len(CATEGORIES), dtype=np.float64)
    standard, adaptive = prior.copy(), prior.copy()
    print(f"Дирихле: {CHUNK_SIZE} событий в чанке, λ={DECAY}; дрейф с чанка {DRIFT_STEP + 1}")
    for step in range(1, STEPS + 1):
        proportions = NORMAL if step <= DRIFT_STEP else DRIFT
        events = rng.choice(len(CATEGORIES), CHUNK_SIZE, p=proportions)
        counts = np.bincount(events, minlength=len(CATEGORIES)).astype(np.int64, copy=False)
        standard = update(prior, standard, counts)
        adaptive = update(prior, adaptive, counts, DECAY)
        if step in (1, DRIFT_STEP, STEPS):
            std_mean, std_sigma = moments(standard)
            adp_mean, adp_sigma = moments(adaptive)
            print(f"\nЧанк {step}; обработано {step * CHUNK_SIZE} событий")
            print("Категория    Истинная   Без забывания E[p] ± std   С забыванием E[p] ± std")
            for name, truth, a, a_sd, b, b_sd in zip(
                CATEGORIES, proportions, std_mean, std_sigma, adp_mean, adp_sigma, strict=True
            ):
                print(f"{name:>9s}    {truth:8.3f}    {a:.3f} ± {a_sd:.3f}              {b:.3f} ± {b_sd:.3f}")
            if step == STEPS:
                err_std = np.abs(std_mean - proportions).sum()
                err_adp = np.abs(adp_mean - proportions).sum()
                print(f"L1-ошибка после дрейфа: {err_std:.3f} без забывания, {err_adp:.3f} с забыванием")


def text_stream() -> Iterator[tuple[list[str], NDArray[np.int64]]]:
    """Yield one batch at a time; bound the run in the consumer."""
    rng = np.random.default_rng(SEED)
    noise = np.array(["worker", "queue", "request", "job", "region", "message"])
    markers = np.array(["sync", "timeout"])
    step = 0
    while True:
        labels = rng.integers(0, 2, size=CHUNK_SIZE, dtype=np.int64)
        opposite = rng.random(CHUNK_SIZE) < 0.10
        feature_class = labels ^ opposite ^ int(step >= DRIFT_STEP)
        context = rng.choice(noise, size=(CHUNK_SIZE, 2))
        texts = [f"{marker} {a} {b}" for marker, (a, b) in zip(markers[feature_class], context, strict=True)]
        yield texts, labels
        step += 1


def text_demo() -> None:
    # Optional for the PDF text version of Practice 5; already project dependencies.
    from itertools import islice

    from sklearn.feature_extraction.text import HashingVectorizer
    from sklearn.naive_bayes import MultinomialNB

    vectorizer = HashingVectorizer(n_features=2**10, alternate_sign=False, norm=None)
    standard, adaptive = MultinomialNB(), MultinomialNB()
    classes = np.array([0, 1])
    correct_standard = correct_adaptive = total_shifted = 0
    print(f"Text NB: предсказываем до partial_fit; дрейф с чанка {DRIFT_STEP + 1}")
    for step, (texts, labels) in enumerate(islice(text_stream(), STEPS), start=1):
        features = vectorizer.transform(texts)
        if step > 1:
            n_standard = int(np.count_nonzero(standard.predict(features) == labels))
            n_adaptive = int(np.count_nonzero(adaptive.predict(features) == labels))
            if step > DRIFT_STEP:
                correct_standard += n_standard
                correct_adaptive += n_adaptive
                total_shifted += labels.size
            if step in (DRIFT_STEP, DRIFT_STEP + 1, DRIFT_STEP + 8, STEPS):
                print(f"Чанк {step}: точность {n_standard / labels.size:.2f} / {n_adaptive / labels.size:.2f}")
            adaptive.class_count_ *= DECAY
            adaptive.feature_count_ *= DECAY
        standard.partial_fit(features, labels, classes=classes)
        adaptive.partial_fit(features, labels, classes=classes)
    print(
        f"Средняя после дрейфа: {correct_standard / total_shifted:.3f} без забывания, "
        f"{correct_adaptive / total_shifted:.3f} с забыванием"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true", help="Run the PDF's streaming text task instead")
    if parser.parse_args().text:
        text_demo()
    else:
        dirichlet_demo()
