# Практика 2: Инкрементальное Бета-Бернулли сопряжение
import numpy as np
from scipy.stats import beta

TRUE_THETA: float = 0.035  
CHUNK_SIZE: int = 10000
STEPS: int = 10

alpha_post: int = 1
beta_post: int = 1

print("Запуск инкрементального байесовского анализа...")
for step in range(STEPS):
    stream_data = np.random.binomial(1, TRUE_THETA, CHUNK_SIZE)
    
    # --- СТУДЕНТ ДОЛЖЕН НАПИСАТЬ КОД НИЖЕ ---
    # 1. Рассчитайте успехи и неудачи в stream_data БЕЗ циклов for.
    successes = int(stream_data.sum())
    failures = CHUNK_SIZE - successes
    # 2. Обновите параметры alpha_post и beta_post.
    alpha_post += successes
    beta_post += failures
    # 3. Рассчитайте границы 95% HDI интервала с помощью квантилей beta.ppf
    ci_low = beta.ppf(0.025, alpha_post, beta_post)
    ci_high = beta.ppf(0.975, alpha_post, beta_post)
    
    if (step + 1) % 10 == 0:
        mean_est = alpha_post / (alpha_post + beta_post)
        print(f"Шаг {step+1}: Оценка θ = {mean_est:.5f} | Интервал: [{ci_low:.5f} - {ci_high:.5f}]")
