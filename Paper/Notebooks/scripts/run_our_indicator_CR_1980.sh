#!/bin/bash

#SBATCH -n 1
#SBATCH -t 00:10:00

activate 368
RUNPATH='D:\Github\Taxonomy-of-novelty'
cd $RUNPATH
python Paper/Notebooks/scripts/create_our_indicator.py --date year --year 1983 --var CR_year_category --start 1 --end 10