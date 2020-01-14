#!/usr/bin/env python3
# Owner         : Squadcast community  
# Purpose       : This script will send job details to Squadcast api service 
# prerequisites : Need to create a service  
# This script has been tested with Python 3.6.

import os
import json
import urllib.request
import argparse

def form_payload(build_id, build_number, job_name, build_url):
    """Forms the python representation of the data payload to be sent from the passed configuration"""
    message = "Build #" + build_number + " failed for " + job_name
    description = "Build #" + build_number + " failed for " + job_name + "\nPlease check detailed logs here: " + build_url + "console"
    payload_rep = {"message" : message , "description" : description}
    return payload_rep

def post_to_url(url, payload):
    """Posts the formed payload as json to the passed url"""
    try:
        req = urllib.request.Request(url, data=bytes(json.dumps(payload), "utf-8"))
        req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req)
        if resp.status > 299:
           print("Request failed with status code %s : %s" % (resp.status, resp.read()))
    except urllib.request.URLError as e:
        if e.code >= 400:
            print("Some error occured while processing the event, ", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Passing build information.')
    parser.add_argument('--url', help='Squadcast API endpoint')
    parser.add_argument('--build_id', help='Build ID of the pipeline')
    parser.add_argument('--build_number', type=int, help='Build number of the pipeline')
    parser.add_argument('--job_name', help='Job name of the pipeline')
    parser.add_argument('--build_url', help='URL of the pipeline job')

    args = parser.parse_args()    

    print("Sending data to squadcast")
    post_to_url(args.url, form_payload(args.build_id, str(args.build_number), args.job_name, args.build_url ))
    print("Done.")