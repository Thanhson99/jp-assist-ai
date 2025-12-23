#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="jp-assist-ai"
PKG_NAME="jp_assist_ai"

mkdir -p "${PROJECT_NAME}"
cd "${PROJECT_NAME}"

# Root files
touch README.md pyproject.toml .gitignore .env.example

# Top-level folders
mkdir -p assets/icons assets/fonts
mkdir -p docs scripts tests/unit tests/integration

# Source tree
mkdir -p "src/${PKG_NAME}"
touch "src/${PKG_NAME}/__init__.py"

mkdir -p "src/${PKG_NAME}/config"
touch "src/${PKG_NAME}/config/settings.py" "src/${PKG_NAME}/config/logging.py"

mkdir -p "src/${PKG_NAME}/core/text" "src/${PKG_NAME}/core/prompts" "src/${PKG_NAME}/core/usecases"
touch "src/${PKG_NAME}/core/models.py" "src/${PKG_NAME}/core/pipeline.py"
touch "src/${PKG_NAME}/core/text/normalizer.py" "src/${PKG_NAME}/core/text/lang_detect.py"
touch "src/${PKG_NAME}/core/prompts/translate.jinja" "src/${PKG_NAME}/core/prompts/rewrite.jinja"
touch "src/${PKG_NAME}/core/usecases/translate_screen.py" \
      "src/${PKG_NAME}/core/usecases/translate_clipboard.py" \
      "src/${PKG_NAME}/core/usecases/rewrite_japanese.py"

mkdir -p "src/${PKG_NAME}/adapters/ocr" \
         "src/${PKG_NAME}/adapters/llm" \
         "src/${PKG_NAME}/adapters/capture" \
         "src/${PKG_NAME}/adapters/hotkeys" \
         "src/${PKG_NAME}/adapters/storage"
touch "src/${PKG_NAME}/adapters/ocr/base.py" \
      "src/${PKG_NAME}/adapters/ocr/tesseract_ocr.py" \
      "src/${PKG_NAME}/adapters/ocr/paddle_ocr.py"
touch "src/${PKG_NAME}/adapters/llm/base.py" \
      "src/${PKG_NAME}/adapters/llm/openai_llm.py" \
      "src/${PKG_NAME}/adapters/llm/local_llm.py"
touch "src/${PKG_NAME}/adapters/capture/base.py" \
      "src/${PKG_NAME}/adapters/capture/mac_capture.py" \
      "src/${PKG_NAME}/adapters/capture/win_capture.py"
touch "src/${PKG_NAME}/adapters/hotkeys/base.py" \
      "src/${PKG_NAME}/adapters/hotkeys/mac_hotkeys.py" \
      "src/${PKG_NAME}/adapters/hotkeys/win_hotkeys.py"
touch "src/${PKG_NAME}/adapters/storage/base.py" \
      "src/${PKG_NAME}/adapters/storage/sqlite_store.py"

mkdir -p "src/${PKG_NAME}/app/overlay" "src/${PKG_NAME}/app/screens" "src/${PKG_NAME}/app/resources"
touch "src/${PKG_NAME}/app/main.py" "src/${PKG_NAME}/app/tray.py"
touch "src/${PKG_NAME}/app/overlay/overlay_window.py" "src/${PKG_NAME}/app/overlay/region_selector.py"
touch "src/${PKG_NAME}/app/screens/settings_window.py" "src/${PKG_NAME}/app/screens/history_window.py"
touch "src/${PKG_NAME}/app/resources/qt_resources.qrc"

mkdir -p "src/${PKG_NAME}/services" "src/${PKG_NAME}/cli"
touch "src/${PKG_NAME}/services/translate_service.py" "src/${PKG_NAME}/services/rewrite_service.py"
touch "src/${PKG_NAME}/cli/main.py"

# Docs + scripts
cat > docs/architecture.md <<'EOF'
# Architecture

- `core/`: business logic thuần (pipeline, usecases, models, prompts).
- `adapters/`: tích hợp OCR/LLM/capture/hotkeys/storage theo interface.
- `app/`: UI (PySide6/Qt) gồm overlay, region select, tray, settings.
- `services/`: glue giữa UI và usecases.
EOF

cat > docs/roadmap.md <<'EOF'
# Roadmap

## MVP (macOS)
1. Hotkey -> chọn vùng màn hình
2. Screenshot vùng -> OCR
3. OCR text -> LLM dịch + giải thích
4. Overlay hiển thị + copy

## V2
- Rewrite JP (business/comtor)
- History + glossary
- Multi-language JP/VI/EN

## V3
- Local LLM option
- Windows support (capture/hotkeys)
EOF

cat > docs/prompts.md <<'EOF'
# Prompts

- `translate.jinja`: dịch + giải thích ngữ cảnh + mức độ lịch sự
- `rewrite.jinja`: sửa ngữ pháp + gợi ý văn phong business/comtor
EOF

cat > scripts/dev_run.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
python -m jp_assist_ai.app.main
EOF
chmod +x scripts/dev_run.sh

cat > scripts/build_mac.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "TODO: add packaging with pyinstaller/briefcase"
EOF
chmod +x scripts/build_mac.sh

cat > scripts/build_win.ps1 <<'EOF'
Write-Output "TODO: add Windows build steps"
EOF

echo "✅ Created project skeleton: ${PROJECT_NAME}"
echo "Next: open README.md and paste the template content from ChatGPT."
