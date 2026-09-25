#!/bin/zsh
cd -- "$(dirname "$0")"
print 'Choose a fictional case: 1 = workspace access, 2 = missing integration records'
read choice
if [[ "$choice" == "2" ]]; then
    PYTHONDONTWRITEBYTECODE=1 python3 trial/rep_walkthrough.py --case integration
else
    PYTHONDONTWRITEBYTECODE=1 python3 trial/rep_walkthrough.py --case access
fi
print '
Press Return to close this window.'
read finish
