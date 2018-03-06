@echo off
echo Updating your requirements files! Assuming your in the correct environment!
echo pip_reqs.txt...
call pip freeze > pip_reqs.txt
echo conda_reqs.txt...
call conda list -e > conda_reqs.txt
echo done!
call git add pip_reqs.txt conda_reqs.txt