#!/bin/sh

/usr/local/google_appengine/appcfg.py upload_data --url=http://localhost:8080/_ah/remote_api --filename=sample_data/supplier.csv --kind=Supplier --config_file=frontend/bulkloader.yaml --noisy 
/usr/local/google_appengine/appcfg.py upload_data --url=http://localhost:8080/_ah/remote_api --filename=sample_data/customer.csv --kind=Customer --config_file=frontend/bulkloader.yaml --noisy 
/usr/local/google_appengine/appcfg.py upload_data --url=http://localhost:8080/_ah/remote_api --filename=sample_data/expense.csv --kind=Expense --config_file=frontend/bulkloader.yaml --noisy