#!/usr/bin/env bash
set -Eeuo pipefail
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE"

if [[ "${1:-}" == "--system-deps" ]]; then
  command -v sudo >/dev/null || { echo "sudo is required for --system-deps" >&2; exit 2; }
  sudo apt-get update
  sudo apt-get install -y python3 python3-venv libreoffice poppler-utils zip unzip
fi

for command_name in python3 libreoffice pdfinfo pdftotext sha256sum unzip zip; do
  command -v "$command_name" >/dev/null || {
    echo "MISSING_DEPENDENCY: $command_name" >&2
    echo "On Ubuntu/Debian run: bash setup_environment.sh --system-deps" >&2
    exit 3
  }
done

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python - <<'PY'
import docx, lxml, matplotlib, numpy, pandas, scipy, sklearn
print("PYTHON_ENV_OK")
print("numpy", numpy.__version__)
print("pandas", pandas.__version__)
print("scipy", scipy.__version__)
print("scikit-learn", sklearn.__version__)
print("matplotlib", matplotlib.__version__)
print("python-docx", docx.__version__)
print("lxml", lxml.__version__)
PY

echo "ENVIRONMENT_READY: $BASE/.venv"
