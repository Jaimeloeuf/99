# Powershell script to start all the services independantly

start powershell {python ./src/public_service.py --port=6000}
start powershell {python ./src/listing_service.py --port=6001}
start powershell {python ./src/user_service.py --port=6002}