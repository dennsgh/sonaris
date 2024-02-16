# mrilabs

## Dependencies

To setup the environment for env variables used in the app

```bash
python etc/env.py
```

To setup dependencies
```
poetry install --no-root
poetry shell
python -m main --hardware-mock
```

## Running MRILabs

Running the app
```
poetry run python -m main
```

Running the app for hardware-mock
```
poetry run python -m main --hardware-mock
```


The generated .env file will look as such:
```
WORKINGDIR='C:/source/mrilabs'
CONFIG='C:/source/mrilabs/etc'
DATA='C:/source/mrilabs/data'
PYTHONPATH='C:\source\mrilabs\frontend\src;C:\source\mrilabs\src'
ASSETS='C:/source/mrilabs/frontend/assets'
LOGS='C:/source/mrilabs/logs'
```