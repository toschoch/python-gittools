@echo off
echo Updating your requirements files with all packages installed in '{env_name}'!
echo create pip_reqs.txt...
call {env_path}\Scripts\pip freeze > pip_reqs.txt
echo create conda_reqs.txt...
call conda -n {env_name} env export > environment.yml
echo done!
call git add pip_reqs.txt conda_reqs.txt