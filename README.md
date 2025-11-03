# Factory Sim

This repository is for a simple Python based factory simulation, this consists of a:

- part - has simple properties for type and complete
- belt - has a size and used to simulate a moving conveyor belt that can hold parts
- worker - picks up parts from the belt, can peek at their belt position to assemble a complete part
- sim - iterates through stepping through simulation time, moving the belt and totting up totals

## Get Going Quickly

Open it up in Codespaces!

### Tools Used

- Github - source control and storing code somewhere accessible.
- Anaconda - python framework used to define a specific set of packages and dependencies to make the apps environment - Micromamba really
- Docker - containerises software needed for creating a development environment and packages up the app.
- Github Actions - used to complete repetitive tasks such as building containers and deploying the app.

### Nuts and Bolts

Each aspect of the development and deployment cycle is in this repo, these include:

- `src` - contains all the source code
- `.github` - the Continuous Integration (CI) needed to build a gitpod environment for development and build and deploy this app! (notice the `.secret` parameters needed so I'm not sharing login details)
- `environment.yaml` - all the packages needed to make the right Anaconda environment ANYWHERE.
- `.gitignore` - a list of everything you don't want in version control.
