set -e
MYPYPATH=$(dirname "$0") mypy --config ./mypy.ini drip/ tests/
