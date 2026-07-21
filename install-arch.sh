#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

sudo pacman -S --needed python python-pip python-virtualenv pacman-contrib flatpak smartmontools

python -m venv .venv
source .venv/bin/activate
python -m pip install .

mkdir -p "$HOME/.local/bin"

cat > "$HOME/.local/bin/sentinel-tools" <<EOF
#!/usr/bin/env bash
exec "$PWD/.venv/bin/sentinel-tools" "\$@"
EOF

chmod +x "$HOME/.local/bin/sentinel-tools"

echo
echo "Sentinel Tools installed."
echo "For Fish, run: fish_add_path ~/.local/bin"
echo "Then run: sentinel-tools menu"
