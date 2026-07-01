import pytest
from app.ingestion.loader import load_document, _extract_company_name
from pathlib import Path


def test_extract_company_name():
    assert _extract_company_name("acme-inc_2024.pdf") == "Acme Inc"
    assert _extract_company_name("foobar_10k.pdf") == "Foobar"


def test_load_document_not_found(tmp_path):
    p = tmp_path / "no_such_file.pdf"
    with pytest.raises(FileNotFoundError):
        load_document(str(p))
