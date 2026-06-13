from app.entities.ship import ShipEntity, MovingState, ObjectType
from app.entities.modules import factory as ModuleFactory
from app.models.ship import ShipModel


class ShipMapper:
    def _dump_state(self, entity: ShipEntity) -> dict[str, any]:
        return {
            'c': entity.counter,
            'crew': entity.crew,
            'hunger': entity.hunger,
            'storage': entity.storage.to_dict(),
            'modules': [{'def': m.module_def.name, 'data': m.to_dict()} for m in entity.modules],
            'hull': entity.hull.to_dict(),
            'xy': [entity.pos.x, entity.pos.y],
            'commands': entity.command_queue.to_dict(),
            'state': entity.state,
            'attached_to_id': entity.attached_to_id,
            'attached_to_type': entity.attached_to_type
        }

    def _load_state(self, entity: ShipEntity, data: dict[str, any]):
        entity.counter = data.get('c', 0)
        entity.crew = data.get('crew', 0)
        entity.hunger = data.get('hunger', 0.0)
        entity.storage.from_dict(data.get('storage', {}))
        entity.pos.x, entity.pos.y = data.get('xy', [0.0, 0.0])
        entity.hull.from_dict(data.get('hull', {}))
        entity.state = MovingState(data.get('state', MovingState.Idle))
        entity.attached_to_id = data.get('attached_to_id', None)
        obj_t = data.get('attached_to_type', None)
        if obj_t:
            entity.attached_to_type = ObjectType(obj_t)
        else:
            entity.attached_to_type = None
        entity.modules = []

        # Грузим модули
        modules_data = data.get('modules', [])
        for item in modules_data:
            entity.add_module(ModuleFactory.load(item['def'], entity, item['data']))

        entity.command_queue.from_dict(data.get('commands', {}))

    def to_dict(self, entity: ShipEntity) -> dict[str, any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['owner_id'] = entity.owner_id
        return data

    def from_dict(self, data: dict[str, any]) -> ShipEntity:
        entity = ShipEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.owner_id = data.get('owner_id', 0)
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: ShipModel) -> ShipEntity:
        entity = ShipEntity()
        entity.id = model.id
        entity.name = model.name
        entity.owner_id = model.owner_id
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: ShipEntity) -> dict[str, any]:
        data = {
            'name': entity.name,
            'state': self._dump_state(entity),
            'owner_id': entity.owner_id
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data