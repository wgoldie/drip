set -e
black drip/
mypy drip/ --config ./mypy.ini
