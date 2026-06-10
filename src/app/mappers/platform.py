from app.entities.platform import PlatformEntity
from app.entities.modules import factory as ModuleFactory
from app.models.platform import PlatformModel


class PlatformMapper:
    def _dump_state(self, entity: PlatformEntity) -> dict[str, any]:
        return {
            'c': entity.counter,
            'storage': entity.storage.to_dict(),
            'modules': [{'def': m.module_def.name, 'data': m.to_dict()} for m in entity.modules],
            #'hull': entity.hull.to_dict()
        }

    def _load_state(self, entity: PlatformEntity, data: dict[str, any]):
        entity.counter = data.get('c', 0)
        entity.storage.from_dict(data.get('storage', {}))
        #entity.hull.from_dict(data.get('hull', {}))
        entity.modules = []

        # Грузим модули
        modules_data = data.get('modules', [])
        for item in modules_data:
            entity.add_module(ModuleFactory.load(item['def'], entity, item['data']))

    def to_dict(self, entity: PlatformEntity) -> dict[str, any]:
        data = self._dump_state(entity)
        data['id'] = entity.id
        data['name'] = entity.name
        data['owner_id'] = entity.owner_id
        data['xy'] = [entity.x, entity.y]
        return data

    def from_dict(self, data: dict[str, any]) -> PlatformEntity:
        entity = PlatformEntity()
        entity.id = data.get('id', 0)
        entity.name = data.get('name', '')
        entity.owner_id = data.get('owner_id', 0)
        entity.x, entity.y = data.get('xy', [0.0, 0.0])
        self._load_state(entity, data)
        return entity
        
    def from_model(self, model: PlatformEntity) -> PlatformEntity:
        entity = PlatformEntity()
        entity.id = model.id
        entity.name = model.name
        entity.owner_id = model.owner_id
        entity.x = model.x
        entity.y = model.y
        self._load_state(entity, model.state)
        return entity

    def to_model_data(self, entity: PlatformEntity) -> dict[str, any]:
        data = {
            'name': entity.name,
            'state': self._dump_state(entity),
            'owner_id': entity.owner_id,
            'x': entity.x,
            'y': entity.y
        }
        if entity.id > 0:
            data['id'] = entity.id
        return data