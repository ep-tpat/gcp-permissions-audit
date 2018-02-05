from google.cloud import storage
import os
import json
import csv
import time


outfile = 'audit-permissions' + time.strftime('%Y%m%d-%H%M%S') + '.csv'

outbucket = input('Name of bucket to upload to: ')
if len(outbucket) < 1:
    print('\nNo bucket name supplied! Exiting...')
    exit()

with open(outfile, 'w', newline='') as outfile:
    out_file = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    out_file.writerow(['Level or Tier'] + ['Project'] + ['User or Account'] + ['Permission'])

    """get organization"""
    print('Fetching Organization...')
    org = os.popen('gcloud organizations list | awk \'{print $2}\' | grep -v ID').read().strip()
    print('Done')

    """query organization permissions and load json elements"""
    orgPermCommand = os.popen('gcloud alpha organizations get-iam-policy {} --format json'.format(org)).read()
    orgInfo = json.loads(orgPermCommand)

    """write organization permissions"""
    for i in range(len(orgInfo['bindings'])):
        for j in range(len(orgInfo['bindings'][i]['members'])):
            out_file.writerow(['Organization'] + [org] + [orgInfo['bindings'][i]['members'][j]] +
                              [orgInfo['bindings'][i]['role']])

    """query projects and load json elements"""
    projList = []
    projListCommand = os.popen('gcloud projects list --format json').read()
    projListData = json.loads(projListCommand)

    """load all projects in list"""
    print('Fetching Project list and writing to file...')
    for item in projListData:
        projList.append(item['projectId'])
    print('Done')

    """query project permissions and load json elements"""
    for p in projList:
        projPermCommand = os.popen('gcloud projects get-iam-policy {} --format json'.format(p)).read()
        projInfo = json.loads(projPermCommand)

        """print project permissions"""
        for i in range(len(projInfo['bindings'])):
            for j in range(len(projInfo['bindings'][i]['members'])):
                out_file.writerow(['Project'] + [p] + [projInfo['bindings'][i]['members'][j]] +
                                  [projInfo['bindings'][i]['role']])

    """query project and load bucket list(s)"""
    print('Fetching Bucket list and writing to file...')
    for project in projList:
        bucketListCommand = os.popen('gsutil ls -p {}'.format(project))
        bucketList = bucketListCommand.read().strip().split('\n')

        """query buckets and load json elements"""
        for bucket in bucketList:
            if len(bucket) < 1:
                continue
            else:
                bucketPermCommand = os.popen('gsutil iam get {0} -p {1}'.format(bucket, project)).read()
                bucketInfo = json.loads(bucketPermCommand)

                """print bucket permissions"""
                if 'bindings' in bucketInfo:
                    for i in range(len(bucketInfo['bindings'])):
                        for j in range(len(bucketInfo['bindings'][i]['members'])):
                            out_file.writerow(['Bucket: ' + bucket] + [project] + [bucketInfo['bindings']
                                              [i]['members'][j]] + [bucketInfo['bindings'][i]['role']])
                else:
                    out_file.writerow(['Bucket: ' + bucket] + [project])
    print('Done')

"""instantiate bucket client"""
client = storage.Client()
bucket = client.get_bucket(outbucket)

"""upload file to bucket"""
blob = bucket.blob(outfile.name)
blob.upload_from_filename(filename=outfile.name)

print('\n{0} has been uploaded to the {1} bucket.'.format(outfile.name, outbucket))
