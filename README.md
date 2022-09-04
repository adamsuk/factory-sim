# Factory Sim

This repository is for a simple Python based factory simulation

## Get Going Quickly

Add the prefix `gitpod.io/#` to this repos URL to get developing and playing with the source code.

## Tools Used

- Github - source control and storing code somewhere accessible.
- Anaconda - python framework used to define a specific set of packages and dependencies to make the apps environment.
- Docker - containerises software needed for creating a development environment and packages up the app.
- Github Actions - used to complete repetitive tasks such as building containers and deploying the app.
- Gitpod - allows quick development without needing to install anything locally.

## Nuts and Bolts

Each aspect of the development and deployment cycle is in this repo, these include:

- `src` - contains all the source code
- `.github` - the Continuous Integration (CI) needed to build a gitpod environment for development and build and deploy this app! (notice the `.secret` parameters needed so I'm not sharing login details)
- `environment.yaml` - all the packages needed to make the right Anaconda environment ANYWHERE.
- `.gitignore` - a list of everything you don't want in version control.
- `.gitpod` and `.gitpod.yml` - all the config and setup needed to allow development using Gitpod.

## Notes
