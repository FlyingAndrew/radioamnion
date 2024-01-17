# Radioamnion
Radioamnion is a python module which simplifies and streamlines for the Radioamnion project. The key features are:
- transforming the audio file to a LED visualisation
- storing the visualisation in multiple formats

## Table of Contents
1. [Links](#links)
2. [Project](#project)
3. [Example](#example)
4. [Installation](#installation)
5. [Code Structure](#code-structure)
6. [ToDo-List](#todo-list)

Radioamnion is a python module which simplifies and streamlines for the Radioamnion project. The key features are:
- transforming the audio file to a LED visualisation
- storing the visualisation in multiple formats

## Links
- Project Webpage: http://radioamnion.net
- GitHub-Page: https://kholzapfel.github.io/radioamnion/
- GitHub-Repro: https://github.com/kholzapfel/radioamnion

## Project
RADIO AMNION: SONIC TRANSMISSIONS OF CARE IN OCEANIC SPACE is a multi-year sound art project for the waters of Earth, commissioning and relaying new compositions by contemporary artists more than 2kms deep with/in the Pacific Ocean. During each full moon, far beyond human perception, the abyssal waters of Cascadia Basin resonate with the deep frequencies and voices of invited artists. All transmissions are relayed in the sea through a submerged neutrino telescope experiment’s calibration system and available here online only during the three days of each full moon.

## Example
```python
import radioamnion

```
For more examples have a lock in the [example folder](./examples).

## Installation

### Prepare Python package
Go to the directory of [this README you are reading](README.md) is placed (basically, to the directory of the [pyproject.toml](pyproject.toml) file, but this should be the same) and run:
```bash
python3 -m build
```
This will create the files located in the folder `.egg-info`.

### Install requirements
To install the required python packages run.
```bash
pip install -r requirements.txt
```

### Install with pip
Run the following command to install the package. In case you are not in the directory of the repository replace `.` with the root directory of the package. 
```bash
pip3 install -U --user -e .
```

# Crontab
For c&p to:
```
37 11 24 7 * /home/odroid/mctl/mctl/mctl_client.py module art START /home/odroid/art/---.csv 2>&1 >> /home/odroid/logs/cron_art.log
```
