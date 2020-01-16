#!/usr/bin/env python3
# Owner         : Squadcast community  
# Purpose       : This script will send job details to Squadcast api service 
# prerequisites : Need to create a service  
# This script has been tested with Python 3.6.

import os
import json
import requests
import argparse
import sys
import json

def form_payload(build_number, job_name, build_url, status):
    """Forms the python representation of the data payload to be sent from the passed configuration"""
    message = "Build #{} {} for {}".format(build_number, status, job_name)
    description = "Build #{} {} for {}. \nPlease check detailed logs here: {}console".format(build_number, status, job_name, build_url)
    payload_rep = {"message" : message , "description" : description}
    return payload_rep

def post_to_url(url, payload):   # TODO: add "status" and "eventID" once Aahel PR gets merged
    """Posts the formed payload as json to the passed url"""
    try:
        headers = {'content-type': 'application/json'}
        req = requests.post(url, data = bytes(json.dumps(payload).encode('utf-8')), headers = headers)
        if req.status_code > 299:
            print("Request failed with status code %s : %s" % (req.status_code, req.content))
    except requests.exceptions.RequestException as e:
            print("Unable to create an incident with Squadcast, ", e)
            sys.exit(2)

def get_job_status(job_url, build_number, username, password):
    """Retrieves the job status from the Jenkins API"""
    try:
        url = "{}{}/api/json".format(job_url, str(build_number))
        res = requests.get(url, auth=(username, password))
        build_status_json = json.loads(res.text)
        return build_status_json["result"]

    except requests.exceptions.RequestException as e:
        print (e)
        sys.exit(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing build information.')
    parser.add_argument('--url', help='Squadcast API endpoint')
    parser.add_argument('--username', help='Jenkins username')
    parser.add_argument('--password', help='Jenkins password')
    parser.add_argument('--build_number', type=int, help='Build number of the pipeline')
    parser.add_argument('--job_name', help='Job name of the pipeline')
    parser.add_argument('--build_url', help='URL of the pipeline job')
    parser.add_argument('--job_url', help='URL of the pipeline job')

    args = parser.parse_args()    

    cur_job_status = get_job_status(args.job_url, args.build_number, args.username, args.password)
    prev_job_status = get_job_status(args.job_url, int(args.build_number)-1, args.username, args.password)

    if (prev_job_status == "SUCCESS" and cur_job_status == "FAILURE"):
        print ("Creating an incident in Squadcast!")
        post_to_url(args.url, form_payload(str(args.build_number), args.job_name, args.build_url, "failed" ))
    elif (prev_job_status == "FAILURE" and cur_job_status == "SUCCESS"):
        print ("Resolving an incident in Squadcast!")
        post_to_url(args.url, form_payload(str(args.build_number), args.job_name, args.build_url, "succeeded" ))
    else:
        print ("Not required to create an incident..")

    print("Done.")