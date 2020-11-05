import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import os

'''
Class for utilizing EC2 service of AWS

TO-DO
    implementar
    - enviar comandos (UserData em run_instances - roda em /)

'''

class Client:

    def __init__(self, region:str):

        self.region = region

        if region == 'us-east-1':
            self.img = 'ami-0817d428a6fb68645'

        elif region == 'us-east-2':
            self.img = 'ami-0dd9f0e7df0f0a138'

        self.my_config = Config(region_name = region)

        self.client = boto3.client('ec2', config=self.my_config)


    """Create Security Group and add permissions

    :name: str with name of security group
    :description: str with small description of secutiry group
    :permissions: list of ports to add in the security group
    
    example of usage:
        createSecurityGrp(client, 'mySecurityGroup', 'A Security Group that I created using boto3', [22, 80, 8080])

    """
    def createSecurityGrp(self, name:str, description:str, permissions:list):

        try:
        
            response = self.client.describe_security_groups(
                Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [name]
                    },
                ])

            if response['SecurityGroups']:
                response = self.client.delete_security_group(GroupName=name)
                print(f'Existent and unused Security Group with same name {name} deleted')

            response = self.client.create_security_group(GroupName=name,
                                                    Description=description)

            security_group_id = response['GroupId']
            print(f'Security Group {name} Created: {security_group_id}')

            permList = []

            for port in permissions:
                permList.append({'IpProtocol': 'tcp',
                                 'FromPort': port,
                                 'ToPort': port,
                                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})

            data = self.client.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=permList)

            print(f'Ingress Successfully Set on ports {permissions}')

        except ClientError as e:
            print(e)
            #pass


    """Launches Images in AWS EC2

    :InsType: type of instance (t2.micro)
    :imgID: Image for booting instance (ami-0817d428a6fb68645) <- this is the AMI for Ubuntu 18.04.5 LTS
    :minC: Minimum of instances to create (1)
    :maxC: Maximum of instances to create (1)
    :key: Key pair for SSH access (None)
    :secGr: Security Group Name to associate with Instance

    :Return: dict described in https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.run_instances

    example of usage:
        response = client.launchInstance()

    """
    def launchInstance(self, name:str, InsType='t2.micro', minC=1, maxC=1, key='Fontes', secGr='default'):
        
        response = self.client.run_instances(ImageId=self.img, 
                                                InstanceType=InsType, 
                                                MinCount=minC, 
                                                MaxCount=maxC, 
                                                KeyName=key,
                                                SecurityGroups=[secGr],
                                                TagSpecifications=[{
                                                    'ResourceType': 'instance',
                                                    'Tags': [
                                                        {
                                                            'Key'  : 'Name',
                                                            'Value':  name
                                                        },
                                                        {
                                                            'Key'  : 'Creator',
                                                            'Value': 'PFontes'
                                                        }
                                                    ]
                                                }]
                                            )

        for instance in response['Instances']:
            print(f'Instance {instance["InstanceId"]} created')


    """Delete the keyPair if exists and Makes a new keyPair
    :name: name of key pair
    
    """
    def makeKeyPair(self, name:str):

        response = self.client.describe_key_pairs(Filters=[
            {
                'Name': 'key-name',
                'Values': [name]
            },
        ])

        if response['KeyPairs']:
            print('Deleting existent Key pair')
            response = self.client.delete_key_pair(KeyName=name)

        print('Generating Key pair')
        response = self.client.create_key_pair(KeyName=name)

        if os.path.exists("keyPair-"+self.region):
            os.remove("keyPair-"+self.region)

        f = open("keyPair-"+self.region, "x")
        f.write(response['KeyMaterial'])
        f.close()