# Powershell script to start all the services independantly

start powershell {python public_service.py --port=6000}
start powershell {python listing_service.py --port=6001}
start powershell {python user_service.py --port=6002}