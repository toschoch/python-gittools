#!/usr/bin/env bash
source activate {env_name} # activates the conda environment
{command} $@ # calls the command
source deactivate