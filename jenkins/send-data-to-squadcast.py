import os
import json
import requests
import argparse
import sys

def form_payload(build_number, job_name, build_url, status):
    """Forms the python representation of the data payload to be sent from the passed configuration"""
    message = "Build #{} {} for {}".format(build_number, status, job_name)
    description = "Build #{} {} for {}. \nPlease check detailed logs here: {}console".format(build_number, status, job_name, build_url)
    
    branch_name = ""
    # Check optional env variable
    if "BRANCH_NAME" in os.environ:
        branch_name = os.environ['BRANCH_NAME']

    payload_rep = {"message" : message , "description" : description, "branch_name" : branch_name,
        "build_url":  build_url, "job_name":  job_name, "build_number":  build_number, "node_name": os.environ['NODE_NAME'],
        "status" : status, "event_id" : job_name}
    return payload_rep

def post_to_url(url, payload):  
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

    build_number = int(os.environ['BUILD_NUMBER'])
    job_name = os.environ['JOB_NAME']
    build_url = os.environ['BUILD_URL']
    job_url = os.environ['JOB_URL']

    args = parser.parse_args()    

    cur_job_status = get_job_status(job_url, build_number, args.username, args.password)
    prev_job_status = get_job_status(job_url, int(build_number)-1, args.username, args.password)

    if (prev_job_status == "SUCCESS" and cur_job_status == "FAILURE"):
        print ("Creating an incident in Squadcast!")
        post_to_url(args.url, form_payload(str(build_number), job_name, build_url, "trigger" ))
    elif (prev_job_status == "FAILURE" and cur_job_status == "SUCCESS"):
        print ("Resolving an incident in Squadcast!")
        post_to_url(args.url, form_payload(str(build_number), job_name, build_url, "resolve" ))
    else:
        print ("Not required to create an incident..")

    print("Done.")
