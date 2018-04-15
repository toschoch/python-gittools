@echo off
echo Updating your requirements files with all packages installed in '{env_name}'!
echo create pip_reqs.txt...
call {env_path}\Scripts\pip freeze > pip_reqs.txt
echo create environment.yml...
call conda env export -n {env_name} > environment.yml
echo done!
call git add pip_reqs.txt environment.yml