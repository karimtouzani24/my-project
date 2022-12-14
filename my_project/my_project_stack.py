import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_kms as kms,
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
            availability_zones=["eu-central-1a", "eu-central-1b"],
            ip_addresses=ec2.IpAddresses.cidr("10.10.10.0/24"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask = 26)],
        )

        # creating a route table for vpc1
        # route_table_vpc1 = ec2.CfnRouteTable(
        #     self, 
        #     "RouteTableVPC1",
        #     vpc_id= vpc1.vpc_id
        # )

        # creating vpc, managment server.
        vpc2 = ec2.Vpc(
            self, 
            "Vpc_M",
            availability_zones=["eu-central-1a", "eu-central-1b"],
            ip_addresses=ec2.IpAddresses.cidr("10.20.20.0/24"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=26,),]
        )

        # # creating a route table for vpc2
        # route_table_vpc2 = ec2.CfnRouteTable(
        #     self, 
        #     "RouteTableVPC2",
        #     vpc_id= vpc2.vpc_id
        # )

        # creating a vpc peering connection.
        cfn_cPCPeering_connection = ec2.CfnVPCPeeringConnection(
            self, 
            "My_vpcPeeringConnection",
            peer_vpc_id= vpc1.vpc_id,
            vpc_id= vpc2.vpc_id
        )

        # creating route 
        # cfn_Route= ec2.CfnRoute(
        #         self,
        #         "RouteVPC1-2",
        #         route_table_id= vpc1.public_subnets[0].route_table.route_table_id,
        #         destination_cidr_block= vpc2.vpc_cidr_block,
        #         vpc_peering_connection_id= cfn_cPCPeering_connection.ref
            # )

        for subnet in vpc1.public_subnets:
            self.cfn_Route= ec2.CfnRoute(
                self,
                id=f"{subnet.node.id} RouteVPC1-2",
                route_table_id= subnet.route_table.route_table_id,
                destination_cidr_block= vpc2.vpc_cidr_block,
                vpc_peering_connection_id= cfn_cPCPeering_connection.ref
            # )
            )

        # cfn_Route= ec2.CfnRoute(
        #         self,
        #         "RouteVPC2-1",
        #         route_table_id= vpc2.public_subnets[1].route_table.route_table_id,
        #         destination_cidr_block= vpc1.vpc_cidr_block,
        #         vpc_peering_connection_id= cfn_cPCPeering_connection.ref
        #     )

        for subnet in vpc2.public_subnets:
            self.cfn_Route= ec2.CfnRoute(
                self,
                id= f"{subnet.node.id} RouteVPC2-1",
                route_table_id= subnet.route_table.route_table_id,
                destination_cidr_block= vpc1.vpc_cidr_block,
                vpc_peering_connection_id= cfn_cPCPeering_connection.ref
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
            peer= ec2.Peer.ipv4("89.99.59.255/24"), #temporarely ip address
            connection= ec2.Port.tcp(22),
            description= "allow ssh, admin ip"
        )
        mngmt_SG.add_ingress_rule(
            peer= ec2.Peer.ipv4("89.99.59.255/24"), #temporarely ip address
            connection= ec2.Port.tcp(3389),
            description= "allow rdp, admin ip"
        )

        # creating NACL for webserver.
        web_NACL= ec2.NetworkAcl(
            self,
            "web_NACL",
            vpc= vpc1,
            subnet_selection= ec2.SubnetSelection(
                subnet_type= ec2.SubnetType.PUBLIC)
        )

        web_NACL.add_entry(
            id= "allow HTTP inbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 100,
            traffic= ec2.AclTraffic.tcp_port(80),
            direction= ec2.TrafficDirection.INGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow HTTP outbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 100,
            traffic= ec2.AclTraffic.tcp_port(80),
            direction= ec2.TrafficDirection.EGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow HTTPS inbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 110,
            traffic= ec2.AclTraffic.tcp_port(443),
            direction= ec2.TrafficDirection.INGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow HTTPS outbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 110,
            traffic= ec2.AclTraffic.tcp_port(443),
            direction= ec2.TrafficDirection.EGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow ephemeral inbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 120,
            traffic= ec2.AclTraffic.tcp_port_range(1024, 65535),
            direction= ec2.TrafficDirection.INGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow ephemerel outbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 120,
            traffic= ec2.AclTraffic.tcp_port_range(1024, 65535),
            direction= ec2.TrafficDirection.EGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        web_NACL.add_entry(
            id= "allow SSH inbound",
            cidr= ec2.AclCidr.any_ipv4(),
            rule_number= 130,
            traffic= ec2.AclTraffic.tcp_port(22),
            direction= ec2.TrafficDirection.INGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        # creating NACL for MNGMT server.
        mngmnt_NACL= ec2.NetworkAcl(
            self,
            "mngmnt_NACL",
            vpc= vpc2,
            subnet_selection= ec2.SubnetSelection(
                subnet_type= ec2.SubnetType.PUBLIC)
        )

        mngmnt_NACL.add_entry(
            id= "allow SSH inbound",
            cidr= ec2.AclCidr.ipv4("192.168.178.1/24"),
            rule_number= 140,
            traffic= ec2.AclTraffic.tcp_port(22),
            direction= ec2.TrafficDirection.INGRESS,
            rule_action= ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow SSH outbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 140,
            traffic = ec2.AclTraffic.tcp_port(22),
            direction = ec2.TrafficDirection.EGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow ephemeral inbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 150,
            traffic = ec2.AclTraffic.tcp_port_range(1024, 65535),
            direction = ec2.TrafficDirection.INGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow ephemeral outbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 150,
            traffic = ec2.AclTraffic.tcp_port_range(1024, 65535),
            direction = ec2.TrafficDirection.EGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow RDP inbound",
            cidr = ec2.AclCidr.ipv4("192.168.178.1/24"), #temporarely ip address 
            rule_number = 160,
            traffic = ec2.AclTraffic.tcp_port(3389),
            direction = ec2.TrafficDirection.INGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow RDP outbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 160,
            traffic = ec2.AclTraffic.tcp_port(3389),
            direction = ec2.TrafficDirection.EGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow HTTP inbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 170,
            traffic = ec2.AclTraffic.tcp_port(80),
            direction = ec2.TrafficDirection.INGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow HTTP outbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 170,
            traffic = ec2.AclTraffic.tcp_port(80),
            direction = ec2.TrafficDirection.EGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow HTTPS inbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 180,
            traffic = ec2.AclTraffic.tcp_port(443),
            direction = ec2.TrafficDirection.INGRESS,
            rule_action = ec2.Action.ALLOW,
        )

        mngmnt_NACL.add_entry(
            id = "allow HTTPS outbound",
            cidr = ec2.AclCidr.any_ipv4(), 
            rule_number = 180,
            traffic = ec2.AclTraffic.tcp_port(443),
            direction = ec2.TrafficDirection.EGRESS,
            rule_action = ec2.Action.ALLOW,
        )

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
            availability_zone= "eu-central-1a",
            machine_image= amzn_linux,
            security_group= webserver_SG,
            key_name= "Karim_KP",
            instance_type= ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO),
            block_devices= [ec2.BlockDevice(
                device_name= "/dev/xvda",
                volume= ec2.BlockDeviceVolume.ebs(
                    volume_size= 8,
                    encrypted= True,
                    delete_on_termination= True,
                )
            )]
        )

        #creating instance, MMGMT serever, windows.
        mngmt_server = ec2.Instance(
            self, 
            "mngmt_instance",
            vpc= vpc2,
            availability_zone= "eu-central-1b",
            machine_image= amzn_windows,
            security_group= mngmt_SG,
            key_name= "Karim_KP",
            instance_type= ec2.InstanceType.of(
                ec2.InstanceClass.T2,
                ec2.InstanceSize.MICRO),
            block_devices= [ec2.BlockDevice(
                device_name= "/dev/sda1",
                volume= ec2.BlockDeviceVolume.ebs(
                    volume_size= 30,
                    encrypted= True,
                    delete_on_termination= True,
                )
            )]
        )

        # creating a bucket
        bucket = s3.Bucket(
            self, 
            "project_bucket",
            bucket_name= "bucket-project-karim24",
            encryption= s3.BucketEncryption.KMS,
            versioned= True,
            removal_policy= cdk.RemovalPolicy.DESTROY,
            auto_delete_objects= True
        )
        # upload a files in the bucket.
        userdate_upload= s3deploy.BucketDeployment(
            self, 
            "DeployS3",
            sources=[s3deploy.Source.asset("./asset-folder")],
            destination_bucket= bucket,
        )
        bucket.grant_read(web_server)

        web_userdata= web_server.user_data.add_s3_download_command(
            bucket= bucket,
            bucket_key= "webserver_userdata.sh",
        )

        web_server.user_data.add_execute_file_command(file_path= web_userdata)

        # web_server.user_data.add_s3_download_command(
        #     bucket= bucket,
        #     bucket_key= "index.html"
        # )

        

        # web_server.user_data.add_commands("chmod 755 -R /var/www/html/")

        # web_server.user_data.add_execute_file_command(file_path= "/var/www/html")
        

        # mngmt_kms = kms.Key(self, "mngmtKey",
            # enable_key_rotation= True,)
        
        # mngmt_key_pair = ec2.CfnKeyPair(
        #     self, 
        #     "MngmtKeyPair",
        #     key_name="mngmtKey",
        # )

        # websrv_key_pair = ec2.CfnKeyPair(
        #     self, 
        #     "WebsrvKeyPair",
        #     key_name="websrvKey",
        # )

        