#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SRC="$ROOT/app"
TST="$ROOT/tests"

# ------------------------------------------------------------------
# Helper: create empty test file while mirroring the source path
# ------------------------------------------------------------------
mk(){
  local layer=$1        # unit | integration | e2e
  local kind=$2         # crud | services | routes | utils | scenarios
  local src_path=$3     # modules/posts/crud/crud_post.py
  local fname
  fname=$(basename "$src_path" .py)_test.py   # crud_post_test.py

  local dir="$TST/$layer/$kind/$(dirname "$src_path")"
  mkdir -p "$dir"
  touch "$dir/$fname"
}

# ------------------------------------------------------------------
# 1.  UNIT –– isolated business logic
# ------------------------------------------------------------------
for mod in \
  core/{config,db,security} \
  shared/{crud/base,deps/deps,exceptions/exceptions,utils/utils} ;
do
  mk unit utils "$mod.py"
done

# modules
for area in \
  ai_features analytics auth content_moderation integrations live_streams \
  media messaging monetization news notifications posts reels search \
  social stories users ;
do
  for f in "$SRC/modules/$area"/crud/*.py; do [[ -f "$f" ]] && mk unit crud "modules/$area/crud/$(basename "$f")"; done
  for f in "$SRC/modules/$area"/services/*.py; do [[ -f "$f" ]] && mk unit services "modules/$area/services/$(basename "$f")"; done
  # optional: model pure unit tests (no DB)
  for f in "$SRC/modules/$area"/model/*.py; do [[ -f "$f" ]] && mk unit models "modules/$area/model/$(basename "$f")"; done
done

# ------------------------------------------------------------------
# 2.  INTEGRATION –– DB / external service
# ------------------------------------------------------------------
for area in \
  ai_features analytics auth content_moderation integrations live_streams \
  media messaging monetization news notifications posts reels search \
  social stories users ;
do
  mk integration repositories "modules/$area/repository_test.py"
  mk integration services    "modules/$area/service_test.py"
done

# ------------------------------------------------------------------
# 3.  E2E –– full HTTP via TestClient
# ------------------------------------------------------------------
for area in \
  ai_features analytics auth content_moderation integrations live_streams \
  media messaging monetization news notifications posts reels search \
  social stories users ;
do
  mk e2e api "modules/$area/api_test.py"
done

# ------------------------------------------------------------------
# 4.  conftest hierarchy
# ------------------------------------------------------------------
mkdir -p "$TST"/{unit,integration,e2e}
touch "$TST/unit/conftest.py"
touch "$TST/integration/conftest.py"
touch "$TST/e2e/conftest.py"

cat > "$TST/conftest.py" <<'EOF'
import os,sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
pytest_plugins = [
    "tests.unit.conftest",
    "tests.integration.conftest",
    "tests.e2e.conftest",
]
EOF

# ------------------------------------------------------------------
# 5.  handy runners
# ------------------------------------------------------------------
cat > "$TST/run_unit.sh" <<'EOF'
#!/usr/bin/env bash
pytest tests/unit -q --cov=app --cov-report=term-missing "$@"
EOF
cat > "$TST/run_integration.sh" <<'EOF'
#!/usr/bin/env/bash
pytest tests/integration -q --cov=app --cov-report=term-missing "$@"
EOF
cat > "$TST/run_e2e.sh" <<'EOF'
#!/usr/bin/env bash
pytest tests/e2e -q --tb=short "$@"
EOF
chmod +x "$TST"/run_*.sh

echo "✅  Test skeleton created under $TST"
tree -L 4 -d "$TST"