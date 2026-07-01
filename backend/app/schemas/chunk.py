try:
    from pydantic import BaseModel
except Exception:
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        def dict(self):
            return self.__dict__

        def copy(self, update=None):
            data = dict(self.__dict__)
            if update:
                data.update(update)
            return type(self)(**data)


class Chunk(BaseModel):

    chunk_id: str

    company: str

    section: str

    start_page: int

    end_page: int

    text: str

    character_count: int

    chunk_index: int