# Radioamnion

Radioamnion is a python module which simplifies and streamlines for the Radioamnion project. The key features are:
- transforming the audio file to a LED visualisation
- storing the visualisation in multiple formats

#### Links
- Project Webpage: http://radioamnion.net
- GitHub-Page: https://flyingandrew.github.io/radioamnion/
- GitHub-Repro: https://github.com/FlyingAndrew/radioamnion

#### Table of Contents
1. [Example](#example)
2. [Installation](#installation)
3. [Code Structure](#code-structure)
4. [ToDo-List](#todo-list)

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

## Code Structure

## TODO List:
* [ ] add examples
* [ ] README

# Crontab
For c&p to:
```
37 11 24 7 * /home/odroid/mctl/mctl/mctl_client.py module art START /home/odroid/art/---.csv 2>&1 >> /home/odroid/logs/cron_art.log
```
