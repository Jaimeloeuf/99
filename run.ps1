# Powershell script to start all the services independantly

start powershell {python user_service.py --port=5000}
start powershell {python listing_service.py --port=6000}