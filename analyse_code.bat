@echo off
pylint --rcfile=pylint.cfg --output-format=parseable --reports=y FreeboxAPI.py > analyse_code.txt