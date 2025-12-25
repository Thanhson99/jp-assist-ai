# Architecture

- `core/`: business logic thuần (pipeline, usecases, models, prompts).
- `adapters/`: tích hợp OCR/LLM/capture/hotkeys/storage theo interface.
- `app/`: UI (PySide6/Qt) gồm tray, region select, annotation canvas, capture window, settings.
- `services/`: glue giữa UI và usecases.
