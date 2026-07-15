class ResourcesPool:
    def __init__(self):
        self._pool: dict[int, int | float] = {}
        self._cache: int | float = 0

    def add(self, id: int, amount: int | float):
        if id not in self._pool or self._pool[id] != amount:
            self._pool[id] = amount
            self._cache = sum(self._pool.values())

    def remove(self, id: int):
        if self._pool.pop(id, None) is not None:
            self._cache = sum(self._pool.values())

    @property
    def value(self):
        return self._cache

    def __str__(self) -> str:
        return str(self._pool)