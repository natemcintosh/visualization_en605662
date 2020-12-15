# README
## Final Project
## Nathan McIntosh

---
### Dependency Installation
This project requires python 3.6+, and the following libraries:
- [pandas](https://pandas.pydata.org/getting_started.html)
- [plotly](https://plotly.com/python/)
- [numpy](https://numpy.org)
- [dash](https://dash.plotly.com)

[Python](https://www.python.org) can be installed a number of ways. If you do not have it installed already, I would suggest using either [homebrew](https://brew.sh) or [miniconda](https://docs.conda.io/en/latest/miniconda.html).

For the libraries, each of the above library links includes information on how to install said package if you do not have it already. If you have [pip](https://pypi.org/project/pip/) installed, I would suggest using that for easy python library management. [Miniconda](https://docs.conda.io/en/latest/miniconda.html) also works well. 

---
### To run
At the command line, within the `final_project` folder, run the command 
```python
python code/app.py
```
This will gather data from the internet (or read cached data), generate figures, and create a locally hosted webpage. The printed dialog at your command line will give you an address to put in your browser. 

To run the program with no cached data, ensure that there is an empty folder called `data`. To run with cached data, rename the `example_data` folder to `data`. **NB: running with no cached data will probably take over 20 minutes, as individual requests for thousands of packages are made to homebrew's API**