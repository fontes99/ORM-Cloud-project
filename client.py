import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import os
import subprocess as sp
from misc import *


class Client:
    '''
    Class for utilizing EC2 service of AWS

    TO-DO
        implementar
        - deletar instancias existentes
        - enviar comandos (UserData em run_instances - roda em /)

    '''

    def __init__(self, region:str):

        self.region = region

        if region == 'us-east-1':
            self.img = 'ami-0817d428a6fb68645'

        elif region == 'us-east-2':
            self.img = 'ami-0dd9f0e7df0f0a138'

        self.my_config = Config(region_name = region)

        self.client = boto3.client('ec2', config=self.my_config)


    def createSecurityGrp(self, name:str, description:str, permissions:list):
        """Create Security Group and add permissions

        :name: str with name of security group
        :description: str with small description of secutiry group
        :permissions: list of ports to add in the security group
        
        example of usage:
            createSecurityGrp(client, 'mySecurityGroup', 'A Security Group that I created using boto3', [22, 80, 8080])
        """

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
                print(f'Existent and unused '+OKGREEN+'Security Group '+ENDC+f'with same name {name} '+WARNING+'deleted'+ENDC)

            response = self.client.create_security_group(GroupName=name,
                                                    Description=description)

            security_group_id = response['GroupId']
            print(OKGREEN+'Security Group '+ENDC+f'{name} Created: {security_group_id}')

            permList = []

            for port in permissions:
                permList.append({'IpProtocol': 'tcp',
                                 'FromPort': port,
                                 'ToPort': port,
                                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})

            data = self.client.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=permList)

            print(f'Ingress Successfully Set on ports {permissions} (HTTPStatusCode: {data["ResponseMetadata"]["HTTPStatusCode"]})')

        except ClientError as e:
            print(e)
            #pass


    def launchInstance(self, name:str, cmd:str, InsType='t2.micro', minC=1, maxC=1, key='Fontes', secGr='default', ):
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
        
        response = self.client.run_instances(ImageId=self.img, 
                                                InstanceType=InsType, 
                                                MinCount=minC, 
                                                MaxCount=maxC, 
                                                KeyName=key,
                                                SecurityGroups=[secGr],
                                                UserData=cmd,
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
            print(OKGREEN+f'Instance {name} ({instance["InstanceId"]}) created'+ENDC)


    def makeKeyPair(self, name:str):
        """Delete the keyPair if exists and Makes a new keyPair
        :name: name of key pair
        """

        filename = name + '.pem'

        response = self.client.describe_key_pairs(Filters=[
            {
                'Name': 'key-name',
                'Values': [name]
            },
        ])

        if response['KeyPairs']:
            print(WARNING+'Deleting existent Key pair'+ENDC)
            response = self.client.delete_key_pair(KeyName=name)

        print(f'Generating '+OKBLUE+'Key pair '+ENDC+f'{name} in file {filename}')
        response = self.client.create_key_pair(KeyName=name)

        if os.path.exists(filename):
            os.remove(filename)

        f = open(filename, "x")
        f.write(response['KeyMaterial'])
        f.close()

        sp.run(f'chmod 400 {filename}', shell=True, check=True)


    def cleanUp(self):
        """ Terminates all instances created by this code
        """
        
        instances_ids = []

        response = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Creator',
                    'Values': [
                        'PFontes',
                    ]
                },
            ])

        for i in range(len(response['Reservations'])):
            instances_ids.append(response['Reservations'][i]['Instances'][0]['InstanceId'])
        
        print(HEADER+UNDERLINE+'Cleaning Up'+ENDC)
        for j in instances_ids:
            print(f'Terminating instance {j}')
            response = self.client.terminate_instances(
                InstanceIds=[j])

