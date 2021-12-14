import boto3
import sys
import jinja2

client = boto3.client('ec2')

for line in sys.stdin:
    
    print(line)
    
    pvc_namespace, pvc_name, pv = line.split(" ")

    response = client.describe_volumes(
        Filters=[
            {
                'Name': 'tag:kubernetes.io/created-for/pv/name',
                'Values': [
                    pv.strip()
                ]
            }
        ]
    )
    
    if len(response['Volumes']) != 1:
        continue
        
    volume = response['Volumes'][0]
    
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("pv.yml.j2")
    outputText = template.render(volume_id=volume['VolumeId'], az=volume['AvailabilityZone'], size=volume['Size'], pvc_name=pvc_name, pvc_namespace=pvc_namespace, pv=pv)
    
    f = open(f"{pv.strip()}.yaml", "w")
    f.write(outputText)
    f.close()