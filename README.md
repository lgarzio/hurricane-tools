# hurricane-tools

## Installation Instructions
Add the channel conda-forge to your .condarc. You can find out more about conda-forge from their website: https://conda-forge.org/

`conda config --add channels conda-forge`

Clone the hurricane-tools repository.

`git clone https://github.com/lgarzio/hurricane-tools.git`

Change your current working directory to the location that you downloaded hurricane-tools. 

`cd /Users/lgarzio/Documents/repo/hurricane-tools/`

Create conda environment from the included environment.yml file:

`conda env create -f environment.yml`

Once the environment is done building, activate the environment:

`conda activate hurricane-tools`