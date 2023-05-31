#!/bin/bash
mkdocs gh-deploy
rm -rf ./site

rm -rf ./dist
rm -rf ./pdocr_rpc.egg-info

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
python3 -m build
twine upload dist/*