# Notes regarding my own implementation

## LEGEND:
- LS: listing service
- US: user service
- PS: Public service / API Aggregator

## Ports used in this application
PS -> 6000
LS -> 6001
US -> 6002

I did not deploy all the services to the same hostname. Instead they are deployed to the same "host" but on different ports.  
All the SQLite databases files are created in the "database/" directory in the root directory.  
Although not recommended in actual production code, since this is a demo, the Database files are also included in the remote repo.  