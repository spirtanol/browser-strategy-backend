class ResourcesPool:
    def __init__(self):
        self._pool: dict[str, int | float] = {}
        self._cache = None

    def add_pool(self, id: str, amount: int | float):
        self._pool[id] = amount
        self._cache = None

    def remove_pool(self, id: str):
        self._pool.pop(id, None)
        self._cache = None

    @property
    def value(self):
        if self._cache is None:
            self._cache = 0
            for d in self._pool.values():
                self._cache += d
        return self._cache

    def to_dict(self) -> dict[str, int | float]:
        return self._pool
    
    def from_dict(self, data: dict[str, int | float]):
        self._pool = data
        self._cache = None

    def __str__(self) -> str:
        return str(self._pool)