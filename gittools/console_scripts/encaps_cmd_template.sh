#!/usr/bin/env bash
source activate {env} # activates the conda environment
{command} $@ # calls the command
source deactivate