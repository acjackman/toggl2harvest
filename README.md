# Toggl2Harvest

Moving data from Toggl personal time tracking to company time tracking in harvest.

```bash
toggl2harvest download-toggl-data
toggl2harvest validate-data
toggl2harvest upload-to-harvest
```

## Install

Install with pip from github:

```bash
pip3 install git+git://github.com/acjackman/toggl2harvest.git
```

## Developing

### Quickstart

#### Setup environment

```bash
pipenv install
```

#### Install for development

```bash
pipenv install -e .
```

#### Run Tests

```bash
pipenv shell pytest
```
