# COMP5703_BTC

## Update log 22, Sep, 2017 
Add pre-processing program and turning point program.

- Due to original raw data is to big to upload to github it has not been added.
- Smooth method for this case in turning point program, is ewm, a few more methods will be tested.
- Please go to [this site](https://www.kaggle.com/mczielinski/bitcoin-historical-data#_=_) to download full data set if you want to try pre-processing.

## Update log 13, Nov, 2017
Update final version of project and data.

- All csv file that has a name start with zigzag will be gerenate by markov_chain_BTC_modified.R.
- Script script_RinPython.python provides a way to chain R script and python scripts, and adding new data from web socket to local file.
- Scripts that has a name start with API utilzes API across different platform to obtain data.


## Usage guide

- To run markov_chain_BTC_modified.R (Markov network prediction model), please modify work directory in code 3 to your local repository.
- A few R packages will be needed, including dplyr, infotheo, caret, RColorBrewer, and infotheo.
- Run turningPoint_confirmation_ewm_smooth.python to see trading simulation and turning point demostration.
