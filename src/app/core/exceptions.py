class ServiceError(Exception):
    pass

class NotFoundEntityError(ServiceError):
    pass

class ShipNotFound(NotFoundEntityError):
    def __init__(self, id: int):
        super().__init__(f"Ship {id} not found")
        self.id = id
