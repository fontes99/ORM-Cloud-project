import boto3
from botocore.exceptions import ClientError

'''
Class for utilizing EC2 service of AWS

TO-DO
    - dar nome para instancias
    - enviar comandos

'''

class Client:

    def __init__(self):
        self.client = boto3.client('ec2')
        self.security_groups = []
        self.updateSecurityGroups()


    """Create Security Group and add permissions

    :name: str with name of security group
    :description: str with small description of secutiry group
    :permissions: list of ports to add in the security group
    
    example of usage:
        createSecurityGrp(client, 'mySecurityGroup', 'A Security Group that I created using boto3', [22, 80, 8080])

    """
    def createSecurityGrp(self, name:str, description:str, permissions:list):

        try:
            self.updateSecurityGroups()
            if name in self.security_groups:
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

            print(f'Ingress Successfully Set {data}')

        except ClientError as e:
            print(e)


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
    def launchInstance(self, InsType='t2.micro', imgID='ami-0817d428a6fb68645', minC=1, maxC=1, key='Fontes', secGr='default'):

        response = self.client.run_instances(ImageId=imgID, 
                                        InstanceType=InsType, 
                                        MinCount=minC, 
                                        MaxCount=maxC, 
                                        KeyName=key,
                                        SecurityGroups=[secGr])

        return response


    """Updates security groups name list for consulting
    """
    def updateSecurityGroups(self):
        response = self.client.describe_security_groups()
        for name in range(len(response['SecurityGroups'])):
            self.security_groups.append(response['SecurityGroups'][name]['GroupName'])

            