set -e
black drip/ tests/
mypy  --config ./mypy.ini drip/ tests/
