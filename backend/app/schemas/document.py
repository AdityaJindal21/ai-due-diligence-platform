try:
    from pydantic import BaseModel
except Exception:  # simple fallback when pydantic not installed
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


class Page(BaseModel):
    page_number: int
    text: str
    character_count: int


class DocumentMetadata(BaseModel):
    company: str
    filename: str
    filing_type: str
    year: int
    source: str
    total_pages: int


class Document(BaseModel):
    metadata: DocumentMetadata
    pages: list[Page]