class ResourcesPool:
    def __init__(self):
        self._pool: dict[int, int | float] = {}
        self._cache = None

    def add(self, id: int, amount: int | float):
        self._pool[id] = amount
        self._cache = None

    def remove(self, id: int):
        self._pool.pop(id, None)
        self._cache = None

    @property
    def value(self):
        if self._cache is None:
            self._cache = sum(self._pool.values())
        return self._cache

    def __str__(self) -> str:
        return str(self._pool)