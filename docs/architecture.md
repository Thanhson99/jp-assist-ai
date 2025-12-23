# Architecture

- `core/`: business logic thuần (pipeline, usecases, models, prompts).
- `adapters/`: tích hợp OCR/LLM/capture/hotkeys/storage theo interface.
- `app/`: UI (PySide6/Qt) gồm overlay, region select, tray, settings.
- `services/`: glue giữa UI và usecases.
