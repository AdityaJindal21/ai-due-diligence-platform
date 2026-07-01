from app.core.pipeline import Pipeline


def process_pdf_job(path: str):
    """Top-level task function for RQ to run. Returns chunk metadata list."""
    p = Pipeline()
    chunks = p.process_pdf(path)
    # return serializable list
    return [c.dict() for c in chunks]
