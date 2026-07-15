class ServiceError(Exception):
    pass

class NotFoundEntityError(ServiceError):
    pass

class TokenInvalidError(Exception):
    pass

class AuthError(Exception):
    pass

class ShipNotFoundError(NotFoundEntityError):
    def __init__(self, id: int):
        super().__init__(f"Ship {id} not found")
        self.id = id

class FleetNotFoundError(NotFoundEntityError):
    def __init__(self, id: int):
        super().__init__(f"Fleet {id} not found")
        self.id = id

class UserNotFoundError(NotFoundEntityError):
    def __init__(self, id: int):
        super().__init__(f"User {id} not found")
        self.id = id

class ServiceNotLoadedError(ServiceError):
    def __init__(self, service_name: str):
        super().__init__(f"Service {service_name} was not loaded")
