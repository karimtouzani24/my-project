import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    Stack,    
)
from constructs import Construct

class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # creating vpc, webserver.
        vpc1 = ec2.Vpc(
            self, 
            "Vpc_W",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.10.10.0/24"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public_subnet_W1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask = 26),
                ec2.SubnetConfiguration(
                    name="Public_subnet_W2",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask= 26)]
        )

        # creating vpc, managment server.
        vpc2 = ec2.Vpc(
            self, 
            "Vpc_M",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.20.20.0/24"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public_subnet_M1",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=26,),
                ec2.SubnetConfiguration(
                    name="Public_subnet_M2",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=26,)]
        )

        # creating a vpc peering connection.
        cfn_cPCPeering_connection = ec2.CfnVPCPeeringConnection(
            self, 
            "My_vpcPeeringConnection",
            peer_vpc_id= vpc1.vpc_id,
            vpc_id= vpc2.vpc_id
        )

        # # creating route 
        # for i in range(0, 1):
        #     ec2.CfnRoute(
        #         self,
        #         "RouteVPC1-2",
        #         route_table_id=,
        #         destination_cidr_block=,
        #         vpc_peering_connection_id=
        #     )

        # for i in range(0, 1):
        #     ec2.CfnRoute(
        #         self,
        #         "RouteVPC2-1",
        #         route_table_id=,
        #         destination_cidr_block=,
        #         vpc_peering_connection_id=
        #     )

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
        web_server = ec2.Instance(
            self, 
            "web_instance",
            vpc= vpc1,
            machine_image= amzn_linux,
            instance_type= ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO)
        )

        #creating instance, MMGMT serever, windows.
        mngmt_server = ec2.Instance(
            self, 
            "mngmt_instance",
            vpc= vpc2,
            machine_image= amzn_windows,
            instance_type= ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO)
        )

        # creating SG webserver
        webserver_SG = ec2.SecurityGroup(
            self, 
            "web_SG",
            vpc=vpc1,
            allow_all_outbound= True,
            description= "webserver security group"
        )

        webserver_SG.add_ingress_rule(
            peer= ec2.Peer.any_ipv4(),
            connection= ec2.Port.tcp(80),
            description= "allow http"
        )

        webserver_SG.add_ingress_rule(
            peer= ec2.Peer.any_ipv4(),
            connection= ec2.Port.tcp(443),
            description= "allow https"
        )

        # creating SG MNGMT server.
        mngmt_SG = ec2.SecurityGroup(
            self, 
            "mngmt_SG",
            vpc= vpc2,
            allow_all_outbound= True,
            description= "mngmt security group"
        )

        mngmt_SG.add_ingress_rule(
            peer= ec2.Peer.any_ipv4(),
            connection= ec2.Port.tcp(80),
            description= "allow http"
        )
        mngmt_SG.add_ingress_rule(
            peer= ec2.Peer.any_ipv4(),
            connection= ec2.Port.tcp(443),
            description= "allow https"
        )
        mngmt_SG.add_ingress_rule(
            peer= ec2.Peer.ipv4("192.168.178.1/24"), #temporarely ip address
            connection= ec2.Port.tcp(22),
            description= "allow ssh, admin ip"
        )
        mngmt_SG.add_ingress_rule(
            peer= ec2.Peer.ipv4("192.168.178.1/24"), #temporarely ip address
            connection= ec2.Port.tcp(3389),
            description= "allow rdp, admin ip"
        )
        
        # creating a bucket
        bucket = s3.Bucket(
            self, 
            "project_bucket",
            bucket_name= "project-bucket",
            encryption= s3.BucketEncryption.KMS,
            versioned= True,
            removal_policy= cdk.RemovalPolicy.DESTROY,
            auto_delete_objects= True
        )
        # s3deploy.BucketDeployment(
        #     self, 
        #     "DeployS3",
        #     sources=[s3deploy.Source.asset("./website-dist?")],
        #     destination_bucket= bucket,
        # )