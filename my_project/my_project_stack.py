from aws_cdk import (
    
    aws_ec2 as ec2,
    Stack,
    
)
from constructs import Construct

class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc1 = ec2.Vpc(self, id="Vpc1",
        max_azs=2,
        ip_addresses=ec2.IpAddresses.cidr("10.10.10.0/24"),
        subnet_configuration=[
            ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=26,
                name="Private-subnet-test"
            )
        ]
        )

        vpc2 = ec2.Vpc(self, id="Vpc2",
        max_azs=2,
        ip_addresses=ec2.IpAddresses.cidr("10.20.20.0/24"),
        subnet_configuration=[
            ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=26,
                name="Private-subnet-test"
            )
        ]
        )
                  