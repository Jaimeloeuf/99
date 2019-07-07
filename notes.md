# Notes on my implementation
This is essentially the README for my own implementation to the Challenge.  


## LEGEND:
- LS: listing service
- US: user service
- PS: Public service / API Aggregator


## Directory Structure
- run.ps1
    - Powershell script to run all 3 services in their own seperate newly created powershells.
    - Using relative path to find the files.
- /src
    - Directory to house all the source code files.
- /databases
    - All the SQLite databases files are created in the "database/" directory in the root directory.
    - Although not recommended in actual production code, since this is a demo, the Database files are also included in the remote repo.
    - Database dir not shown in GH because none of the files are uploaded as gitignore ignores them, meaning that if there is no files, you cannot push a empty directory to the remote repository.
    - Maybe create like a README file in that directory so that the dir can be pushed, and the README will explain what it is for.


## Ports
Since ports were variables defined in the "if __main__" block, I am assuming that all the services should be deployed to the same host, but simply listen to different ports. Thus I used the different ports as listed below to run the 3 services, and these ports are fed into the services automatically when the "run.ps1" script is used to start the services.  
Ports used in this application:  
- PS -> 6000
- LS -> 6001
- US -> 6002