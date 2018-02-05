import os
import json


def main():
    """print CSV Headers"""
    print('Level or Tier,Project,User or Account,Permission')
    get_org_permissions(get_org())
    get_project_permissions(get_projects())
    get_bucket_permissions(get_projects())


def get_org():
    """get organization"""
    org = os.popen('gcloud organizations list | awk \'{print $2}\' | grep -v ID').read().strip()

    return org


def get_org_permissions(org):
    """query organization permissions and load json elements"""
    orgPermCommand = os.popen('gcloud alpha organizations get-iam-policy {} --format json'.format(org)).read()
    orgInfo = json.loads(orgPermCommand)

    """print organization permissions"""
    for i in range(len(orgInfo['bindings'])):
        for j in range(len(orgInfo['bindings'][i]['members'])):
            print('Organization' + ',' + org + ',' + orgInfo['bindings'][i]['members'][j] +
                  ',' + orgInfo['bindings'][i]['role'])

    return ()


def get_projects():
    """query projects and load json elements"""
    projList = []
    projListCommand = os.popen('gcloud projects list --format json').read()
    projListData = json.loads(projListCommand)

    """load all projects in list"""
    for item in projListData:
        projList.append(item['projectId'])

    return projList


def get_project_permissions(projList):
    """query project permissions and load json elements"""
    for p in projList:
        projPermCommand = os.popen('gcloud projects get-iam-policy {} --format json'.format(p)).read()
        projInfo = json.loads(projPermCommand)

        """print project permissions"""
        for i in range(len(projInfo['bindings'])):
            for j in range(len(projInfo['bindings'][i]['members'])):
                print('Project' + ',' + p + ',' + projInfo['bindings'][i]['members'][j] +
                      ',' + projInfo['bindings'][i]['role'])

    return ()


def get_bucket_permissions(projList):
    """query project and load bucket list(s)"""
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
                            print(project + ',Bucket: ' + bucket + ',' + bucketInfo['bindings'][i]['members'][j] +
                                  ',' + bucketInfo['bindings'][i]['role'])
                else:
                    print(project + ',Bucket: ' + bucket)


if __name__ == "__main__":
    main()
