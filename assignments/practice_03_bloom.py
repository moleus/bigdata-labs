# Практика 3: Реализация Фильтра Блума
import math
import hashlib

class BloomFilter:
    def __init__(self, expected_elements: int, false_positive_rate: float) -> None: # Добавлено -> None
        self.n: int = expected_elements
        self.p: float = false_positive_rate
        # --- СТУДЕНТ ДОЛЖЕН НАПИСАТЬ КОД НИЖЕ ---
        # Рассчитайте оптимальные m (self.m) и k (self.k) по формулам из лекции
        self.m: int = math.ceil(-self.n * math.log(self.p) / math.log(2) ** 2)
        self.k: int = max(1, round(self.m / self.n * math.log(2)))
        
        self.bit_array: bytearray = bytearray(math.ceil(self.m / 8))
        print(f"Инициализирован фильтр Блума: m={self.m}, k={self.k}")
        
    def _get_hashes(self, item: str) -> list[int]: # Добавлено -> list[int]
        indices: list[int] = []
        for i in range(self.k):
            raw_hash = hashlib.md5(f"{item}_{i}".encode('utf-8')).hexdigest()
            indices.append(int(raw_hash, 16) % self.m)
        return indices

    def add(self, item: str) -> None: # Добавлено -> None
        # Реализуйте установку битов в 1 с помощью побитовых масок и сдвигов
        for index in self._get_hashes(item):
            self.bit_array[index // 8] |= 1 << (index % 8)

    def contains(self, item: str) -> bool: # Добавлено -> bool
        # Реализуйте проверку наличия битов. Верните False, если встречен 0.
        for index in self._get_hashes(item):
            if not self.bit_array[index // 8] & (1 << (index % 8)):
                return False
        return True

bf = BloomFilter(5000, 0.01)
bf.add("test_session_1")
print(f"Тест добавления сессии: {bf.contains('test_session_1')}")

# Заполняем фильтр до расчётного объёма и проверяем ложные срабатывания на новых ключах
for i in range(bf.n):
    bf.add(f"session_{i}")
false_negatives = sum(not bf.contains(f"session_{i}") for i in range(bf.n))
trials = 20000
false_positives = sum(bf.contains(f"unknown_{i}") for i in range(trials))
print(f"Ложные отрицания: {false_negatives}")
print(f"Доля ложных срабатываний: {false_positives / trials:.4f} (заданная p = {bf.p})")
