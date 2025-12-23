# JP Assist AI

JP Assist AI is a desktop application powered by AI, designed to assist Japanese translation and writing in **IT and business (comtor) environments**.  
It runs directly on the user's machine and enables **on-screen translation**, **context-aware explanation**, and **Japanese business writing assistance**.

In daily work, it is unavoidable to encounter Japanese tasks, specifications, or documents—sometimes long, dense, and full of technical or business terminology. JP Assist AI helps users quickly understand what a task really means, not just translate it word by word.

---

## Key Features

- **On-screen translation**
  - Translate text directly from the screen (web pages, tasks, PDFs, images) using OCR.
  - No copy–paste required.

- **Context-aware translation**
  - Provides not only the translated text, but also:
    - Clear explanation of meaning
    - Usage context (IT / business)
    - Politeness level (casual / business / keigo)

- **Japanese writing assistant**
  - Detects grammar issues and inappropriate expressions.
  - Suggests improved sentences suitable for:
    - Business communication
    - Comtor communication
    - Technical discussions

- **Multi-language support**
  - Japanese ↔ Vietnamese ↔ English
  - Translation is meaning-based, not word-by-word.

---

## MVP Scope (macOS First)

1. Global hotkey → select screen region  
2. Capture selected region → OCR  
3. OCR text → AI translation + explanation  
4. Display result in an overlay / popup with copy support  

---

## Project Structure

jp-assist-ai/
├─ README.md
├─ pyproject.toml                 # Dependency management (poetry / uv / pip-tools)
├─ .env.example                   # Environment variable template (API keys, models, etc.)
├─ .gitignore
├─ assets/
│  ├─ icons/
│  └─ fonts/
├─ docs/
│  ├─ architecture.md
│  ├─ roadmap.md
│  └─ prompts.md                  # Prompt templates and guidelines
├─ scripts/
│  ├─ dev_run.sh                  # Run app in development mode
│  ├─ build_mac.sh                # macOS build script
│  └─ build_win.ps1               # Windows build script
├─ tests/
│  ├─ unit/
│  └─ integration/
└─ src/
   └─ jp_assist_ai/
      ├─ __init__.py
      ├─ config/
      │  ├─ settings.py           # Load env vars, app config, feature flags
      │  └─ logging.py            # Logging configuration
      ├─ core/                    # Pure business logic (OS/UI independent)
      │  ├─ models.py             # Dataclasses: OCRResult, TranslationResult, Suggestion, etc.
      │  ├─ pipeline.py           # Orchestration: screenshot → OCR → AI → render-ready data
      │  ├─ text/
      │  │  ├─ normalizer.py      # Clean OCR text (full-width/half-width, newlines, noise)
      │  │  └─ lang_detect.py     # Language detection
      │  ├─ prompts/
      │  │  ├─ translate.jinja    # Translation + explanation prompt
      │  │  └─ rewrite.jinja      # Business/comtor rewrite prompt
      │  └─ usecases/
      │     ├─ translate_screen.py
      │     ├─ translate_clipboard.py
      │     └─ rewrite_japanese.py
      ├─ adapters/                # External integrations (OCR / LLM / OS)
      │  ├─ ocr/
      │  │  ├─ base.py            # OCR interface
      │  │  ├─ tesseract_ocr.py
      │  │  └─ paddle_ocr.py
      │  ├─ llm/
      │  │  ├─ base.py            # LLM interface
      │  │  ├─ openai_llm.py
      │  │  └─ local_llm.py       # Optional: llama.cpp / Ollama
      │  ├─ capture/
      │  │  ├─ base.py            # Screen capture interface
      │  │  ├─ mac_capture.py     # mss + macOS permission handling
      │  │  └─ win_capture.py
      │  ├─ hotkeys/
      │  │  ├─ base.py            # Global hotkey interface
      │  │  ├─ mac_hotkeys.py
      │  │  └─ win_hotkeys.py
      │  └─ storage/
      │     ├─ base.py            # Storage interface
      │     └─ sqlite_store.py    # History, glossary, cache
      ├─ app/                     # UI layer (PySide6 / Qt)
      │  ├─ main.py               # UI entry point
      │  ├─ tray.py               # Menu bar / tray application
      │  ├─ overlay/
      │  │  ├─ overlay_window.py  # Translation popup / overlay window
      │  │  └─ region_selector.py # Screen region selection
      │  ├─ screens/
      │  │  ├─ settings_window.py
      │  │  └─ history_window.py
      │  └─ resources/
      │     └─ qt_resources.qrc
      ├─ services/                # Glue code connecting UI and core use cases
      │  ├─ translate_service.py
      │  └─ rewrite_service.py
      └─ cli/
         └─ main.py               # Quick CLI testing (translate image/text from terminal)

### Design Principles
- **Separation of concerns**: UI, business logic, and external integrations are clearly separated.
- **Cross-platform ready**: macOS first, Windows support planned.
- **Replaceable components**: OCR engine, LLM provider, and UI can be swapped easily.

---

## Processing Pipeline
Screen Region Selection
- **Screen Capture**
- **OCR**
- **Text Normalization**
- **AI Translation / Explanation / Rewrite**
- **Overlay Rendering**


---

## Tech Stack (Planned)

- **UI**: PySide6 (Qt)
- **Screen capture**: mss / native macOS APIs
- **OCR**: PaddleOCR or Tesseract
- **AI / LLM**:
  - Cloud: OpenAI / Claude
  - Local (optional): llama.cpp / Ollama
- **Storage**: SQLite (history, glossary, cache)

---

## Development (Temporary)

```bash
./scripts/dev_run.sh
```

> Note: This is a temporary development entry point and may change as the project evolves.

---

## Roadmap

See docs/roadmap.md for detailed milestones.

---

## macOS Permissions

The following permissions are required on macOS:

- Screen Recording: required for screen capture and OCR.
- Accessibility: may be required for global hotkeys and overlay interactions.

---

## License

TBD