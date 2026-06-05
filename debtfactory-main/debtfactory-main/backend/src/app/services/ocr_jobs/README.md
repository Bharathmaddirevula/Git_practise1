# OCR Jobs Service

Asynchronous optical character recognition over uploaded documents, backed by
**Celery + Redis**.

## Flow

```
POST /ocr-jobs/jobs  ->  OcrJob (pending)  ->  Celery task run_ocr
                                                  |
                       OcrEngine.extract_text(...) |  ArtifactStore.get(uri)
                                                  v
                              OcrResult (text)  ->  GET /ocr-jobs/jobs/{id}/result
```

- **Workers** (`workers/celery_app.py`, `workers/tasks.py`) — the Celery app and
  the `run_ocr` task (`ocr_jobs.run_ocr`).
- **Engines** (`engines/base.py`) — pluggable OCR backends (Tesseract, a cloud
  OCR API) implementing the `OcrEngine` protocol.
- **Storage** (`storage/base.py`) — pluggable artifact store for input documents
  and extracted results.

## Endpoints

| Method | Path                          | Purpose                         |
| ------ | ----------------------------- | ------------------------------- |
| POST   | `/ocr-jobs/jobs`              | Submit a document; returns 202. |
| GET    | `/ocr-jobs/jobs/{job_id}`     | Poll job status.                |
| GET    | `/ocr-jobs/jobs/{job_id}/result` | Fetch extracted text.        |

## Configuration

`OcrSettings` (`OCR_` env prefix) in [`config.py`](config.py): Celery broker /
result backend, default engine, artifact storage root.

## Models

`OcrJob` and `OcrResult` in [`models.py`](models.py).
