import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    Stack,    
)
from constructs import Construct

class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc1 = ec2.Vpc(self, "Vpc_W",
        max_azs=2,
        ip_addresses=ec2.IpAddresses.cidr("10.10.10.0/24"),
        subnet_configuration=[
            ec2.SubnetConfiguration(
                name="Public_subnet_W1",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask = 26
            ),
            ec2.SubnetConfiguration(
                name="Public_subnet_W2",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask= 26
            )
        ])

        vpc2 = ec2.Vpc(self, "Vpc_M",
        max_azs=2,
        ip_addresses=ec2.IpAddresses.cidr("10.20.20.0/24"),
        subnet_configuration=[
            ec2.SubnetConfiguration(
                name="Public_subnet_M1",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=26,
            ),
            ec2.SubnetConfiguration(
                name="Public_subnet_M2",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=26,
            )
        ])

        cfn_cPCPeering_connection = ec2.CfnVPCPeeringConnection(self, "My_vpcPeeringConnection",
        peer_vpc_id="Vpc_M",
        vpc_id="Vpc_W")

        # creating linux AMI for the WEB server.
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
       
       #creating Windows Ami for the MGMT server.
        amzn_windows = ec2.MachineImage.latest_windows(
            version=ec2.WindowsVersion.WINDOWS_SERVER_2022_ENGLISH_FULL_BASE
       )

       #creating instance, WEB server, linux.
        web_server = ec2.Instance(self, "web_instance",
        vpc=vpc1,
        machine_image=amzn_linux,
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.T2,
        ec2.InstanceSize.MICRO))

        #creating instance, MMGMT serever, windows.
        mngmt_server = ec2.Instance(self, "mngmt_instance",
        vpc=vpc2,
        machine_image=amzn_windows,
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.T2,
        ec2.InstanceSize.MICRO))
       
        
                  