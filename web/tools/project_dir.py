from pathlib import Path

PROJECT_NAME = 'tennis-scoreboard-project'
PROJECT_DIRECTORY = Path(__file__)

while PROJECT_DIRECTORY.name != PROJECT_NAME:
    PROJECT_DIRECTORY = PROJECT_DIRECTORY.parent
