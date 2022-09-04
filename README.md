# Flask Boilerplate

This repository is a collection of everything needed to get off the ground with Flask.

## Get Going Quickly

To get going with this repo and get developing I recommend:

1 - create your own github account

2 - fork this repo (optional but means you can store any changes you make)

3 - add the prefix `gitpod.io/#` to this repos URL to get developing (remember to use your forked repo if you completed that step)

## Tools Used

- Flask - python web framework that provides functions to make developing a web application easier.
- Github - source control and storing code somewhere accessible.
- Anaconda - python framework used to define a specific set of packages and dependencies to make the apps environment.
- Docker - containerises software needed for creating a development environment and packages up the app.
- Github Actions - used to complete repetitive tasks such as building containers and deploying the app.
- Gitpod - allows quick development without needing to install anything locally.
- Heroku - platform for deploying the app.

## Nuts and Bolts

Each aspect of the development and deployment cycle is in this repo, these include:

- `src` - the source code directory. This has a few snippets of code for simple Flask services (including templates using Jinja2)
- `.github` - the Continuous Integration (CI) needed to build a gitpod environment for development and build and deploy this app! (notice the `.secret` parameters needed so I'm not sharing login details)
- `Dockerfile` - everything needed to spin up the Anaconda environment and containerise the app for deployment.
- `environment.yaml` - all the packages needed to make the right Anaconda environment ANYWHERE.
- `docker-compose.yaml` - a nice little tool to make local development easier. Just run `docker-compose up -d` to spin up the app defined in the `Dockerfile` locally.
- `.gitignore` - a list of everything you don't want in version control.
- `.gitpod` and `.gitpod.yml` - all the config and setup needed to allow development using Gitpod.

## Notes

Slides avaliable [here](https://docs.google.com/presentation/d/1fPhJEUKH6xeVI-9MEIO7NICGmURfDsTg64Hayw9e8-U/edit?usp=sharing)
