import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import os
import time
import subprocess as sp

from .misc import Color


c = Color()


class Client:
    '''
    Class for utilizing EC2 service of AWS

    '''

    def __init__(self, region:str):

        self.region = region

        if region == 'us-east-1':
            self.img = 'ami-0817d428a6fb68645'

        elif region == 'us-east-2':
            self.img = 'ami-0dd9f0e7df0f0a138'

        self.my_config = Config(region_name = region)

        self.client = boto3.client('ec2', config=self.my_config)

        self.loadbalancer = boto3.client('elb', config=self.my_config)

        self.autoscaling = boto3.client('autoscaling', config=self.my_config)


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
                print(f'Existent and unused '+c.OKGREEN+'Security Group '+c.ENDC+f'with same name {name} '+c.WARNING+'deleted'+c.ENDC)

            response = self.client.create_security_group(GroupName=name,
                                                    Description=description)

            security_group_id = response['GroupId']
            print(c.OKGREEN+'Security Group '+c.ENDC+f'{name} Created: {security_group_id}')

            permList = []

            for port in permissions:
                permList.append({'IpProtocol': 'tcp',
                                 'FromPort': port,
                                 'ToPort': port,
                                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]})

            data = self.client.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=permList)

            print(f'Ingress Successfully Set on ports {permissions} (HTTPStatusCode: {data["ResponseMetadata"]["HTTPStatusCode"]})')

            return security_group_id

        except ClientError as e:
            print(e)

            response = self.client.describe_security_groups(
                Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [name]
                    },
                ])

            return response['SecurityGroups'][0]['GroupId']



    def launchInstance(self, name:str, cmd:str, InsType='t2.micro', key='Fontes', secGr='default'):
        """Launches Images in AWS EC2

        :InsType: type of instance (t2.micro)
        :imgID: Image for booting instance (ami-0817d428a6fb68645) <- this is the AMI for Ubuntu 18.04.5 LTS
        :key: Key pair for SSH access (None)
        :secGr: Security Group Name to associate with Instance

        :Return: dict described in https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.run_instances

        example of usage:
            response = client.launchInstance()
        """

        response = self.client.allocate_address()
        floating_ip = response['PublicIp']

        response = self.client.run_instances(
            ImageId=self.img,
            InstanceType=InsType,
            MinCount=1,
            MaxCount=1,
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

        instance_id = response['Instances'][0]["InstanceId"]

        print(c.OKCYAN +f'Booting instance {name} ...'+ c.ENDC)

        # Waiter
        waiter = self.client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance_id])

        response = self.client.associate_address(
            InstanceId=instance_id,
            PublicIp=floating_ip,
        )

        print(c.OKGREEN+f'Instance {name} ({instance_id}) created with PublicIP: {floating_ip}'+c.ENDC)

        return floating_ip



    def makeKeyPair(self, name:str):
        """Delete the keyPair if exists and Makes a new keyPair
        :name: name of key pair
        """

        filename = 'keys/'+name+'.pem'

        response = self.client.describe_key_pairs(Filters=[
            {
                'Name': 'key-name',
                'Values': [name]
            },
        ])

        if response['KeyPairs']:
            print(c.WARNING+'Deleting existent Key pair'+c.ENDC)
            response = self.client.delete_key_pair(KeyName=name)

        print(f'Generating '+c.OKBLUE+'Key pair '+c.ENDC+f'{name} in file {filename}')
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
        instances_ips = []

        response = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Creator',
                    'Values': [
                        'PFontes',
                    ]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running',
                    ]
                },
            ])

        if response['Reservations']:

            for i in response['Reservations']:
                instances_ids.append(i['Instances'][0]['InstanceId'])
                instances_ips.append(i['Instances'][0]['PublicIpAddress'])

            print(c.HEADER+f'Cleaning Up [{self.region}]'+c.ENDC)

            for ip in instances_ips:   

                response = self.client.describe_addresses(
                    PublicIps=[ip]
                )

                allocation_id = response['Addresses'][0]['AllocationId']   

                response = self.client.release_address(
                    AllocationId=allocation_id,
                )

            for id in instances_ids:
                print(f'Terminating instance {id}')

                response = self.client.terminate_instances(
                    InstanceIds=[id]
                )
                
                waiter = self.client.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[id])


    def create_lb(self):

        try:
            response = self.loadbalancer.describe_load_balancers(
                LoadBalancerNames=[
                    'myLoadBalancer',
                ],
            )

            if response['LoadBalancerDescriptions']:
                self.loadbalancer.delete_load_balancer(
                    LoadBalancerName='myLoadBalancer'
                )

                print("Deleting existent loadbalancer 'myLoadBalancer'")
                time.sleep(120)
        except:
            pass
        
        sec_id = self.createSecurityGrp('lb-secgroup', 'oi', [80,8080])

        response = self.loadbalancer.create_load_balancer(
            LoadBalancerName='myLoadBalancer',
            Listeners=[
                {
                    'Protocol': 'TCP',
                    'LoadBalancerPort': 80,
                    'InstancePort': 8080,
                },
            ],
            AvailabilityZones=[
                'us-east-1a','us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f'
            ],
            SecurityGroups=[
                sec_id,
            ],
            Tags=[
                {
                    'Key': 'Creator',
                    'Value': 'PFontes'
                },
            ]
        )

        print(c.OKGREEN+f"Loadbalancer {response['DNSName']} created"+c.ENDC)

        return response['DNSName']

    def autoscale(self):

        response = self.autoscaling.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                'my-auto-scaling-group',
            ]
        )

        if response['AutoScalingGroups']:

            self.autoscaling.delete_auto_scaling_group(
                AutoScalingGroupName='my-auto-scaling-group',
                ForceDelete=True
            )

            print(c.OKCYAN+"Deleting existent autoscaling group 'my-auto-scaling-group'..."+c.ENDC)

            time.sleep(180)


        response = self.autoscaling.describe_launch_configurations(
            LaunchConfigurationNames=[
                'my-auto-scaling-group',
            ]
        )

        if response['LaunchConfigurations']:

            self.autoscaling.delete_launch_configuration(
                LaunchConfigurationName='my-auto-scaling-group'
            )


        response = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        'Django'
                    ]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running',
                    ]
                }
            ]
        )

        django_id = response['Reservations'][0]['Instances'][0]['InstanceId']


        self.autoscaling.create_auto_scaling_group(
            AutoScalingGroupName='my-auto-scaling-group',
            LoadBalancerNames=[
                'myLoadBalancer',
            ],
            InstanceId=django_id,
            MaxSize=5,
            MinSize=1
        )

        print(c.OKGREEN+"'my-auto-scaling-group' group created."+c.ENDC)
