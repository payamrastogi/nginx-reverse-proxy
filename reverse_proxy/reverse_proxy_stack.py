import os
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2
)
from . import config
from constructs import Construct
import base64

my_local_file = os.path.join(os.path.dirname(__file__), 'script/user_data.sh')
with open(my_local_file, "r") as f:
    user_data = f.read()
    user_data_bytes = user_data.encode('ascii')
    base64_bytes = base64.b64encode(user_data_bytes)
    base64_message = base64_bytes.decode('ascii')

class ReverseProxyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # create VPC
        self.reverse_proxy_vpc = aws_ec2.Vpc(
            self,
            config.VPC,
            cidr='10.0.0.0/16',
            nat_gateways=0,
            subnet_configuration=[],
            enable_dns_support=False,
            enable_dns_hostnames=False,
        )
        self.internet_gateway = self.attach_internet_gateway()

        self.subnet_id_to_subnet_map = {}
        self.route_table_id_to_route_table_map = {}
        self.security_group_id_to_group_map = {}
        self.instance_id_to_instance_map = {}

        self.create_route_tables()
        self.create_security_groups()

        self.create_subnets()
        self.create_subnet_route_table_associations()

        self.create_routes()
        self.create_instances()

    def attach_internet_gateway(self) -> aws_ec2.CfnInternetGateway:
        """ Create and attach internet gateway to the VPC """
        internet_gateway = aws_ec2.CfnInternetGateway(self, config.INTERNET_GATEWAY)
        aws_ec2.CfnVPCGatewayAttachment(self,
                                        'internet-gateway-attachment',
                                        vpc_id=self.reverse_proxy_vpc.vpc_id,
                                        internet_gateway_id=internet_gateway.ref)
        return internet_gateway

    def create_route_tables(self):
        """ Create Route Tables """
        for route_table_id in config.ROUTE_TABLES_ID_TO_ROUTES_MAP:
            self.route_table_id_to_route_table_map[route_table_id] = aws_ec2.CfnRouteTable(
                self,
                route_table_id,
                vpc_id=self.reverse_proxy_vpc.vpc_id,
                tags=[{'key': 'Name', 'value': route_table_id}]
            )

    def create_routes(self):
        """ Create routes of the Route Tables """
        for route_table_id, routes in config.ROUTE_TABLES_ID_TO_ROUTES_MAP.items():
            for i in range(len(routes)):
                route = routes[i]

                kwargs = {
                    **route,
                    'route_table_id': self.route_table_id_to_route_table_map[route_table_id].ref,
                }

                if route['router_type'] == aws_ec2.RouterType.GATEWAY:
                    kwargs['gateway_id'] = self.internet_gateway.ref

                del kwargs['router_type']

                aws_ec2.CfnRoute(self, f'{route_table_id}-route-{i}', **kwargs)

    def create_subnets(self):
        """ Create subnets of the VPC """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            subnet = aws_ec2.CfnSubnet(
                self, \
                subnet_id, \
                vpc_id=self.reverse_proxy_vpc.vpc_id, \
                cidr_block=subnet_config['cidr_block'], \
                availability_zone=subnet_config['availability_zone'], \
                tags=[{'key': 'Name', 'value': subnet_id}], \
                map_public_ip_on_launch=subnet_config['map_public_ip_on_launch'], \
            )
            self.subnet_id_to_subnet_map[subnet_id] = subnet

    def create_subnet_route_table_associations(self):
        """ Associate subnets with route tables """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            route_table_id = subnet_config['route_table_id']

            aws_ec2.CfnSubnetRouteTableAssociation(
                self, \
                f'{subnet_id}-{route_table_id}', \
                subnet_id=self.subnet_id_to_subnet_map[subnet_id].ref, \
                route_table_id=self.route_table_id_to_route_table_map[route_table_id].ref
            )

    def create_security_groups(self):
        """ Creates all the security groups """
        for security_group_id, sg_config in config.SECURITY_GROUP_ID_TO_CONFIG.items():
            self.security_group_id_to_group_map[security_group_id] = aws_ec2.CfnSecurityGroup(
                self, \
                security_group_id, \
                vpc_id=self.reverse_proxy_vpc.vpc_id, \
                **sg_config
            )

    def create_instances(self):
        """ Creates all EC2 instances """
        for subnet_id, subnet_config in config.SUBNET_CONFIGURATION.items():
            subnet = self.subnet_id_to_subnet_map[subnet_id]

            self.create_instances_for_subnet(subnet, subnet_config.get('instances', {}))

    def create_instances_for_subnet(self, subnet: aws_ec2.CfnSubnet, instance_id_to_config_map: {str: dict}):
        """ Creates EC2 instances in a subnet """
        for instance_id, instance_config in instance_id_to_config_map.items():
            instance = self.create_instance(subnet, instance_id, instance_config)
            self.instance_id_to_instance_map[instance_id] = instance

    def create_instance(self, subnet: aws_ec2.CfnSubnet, instance_id: str, instance_config: dict) \
            -> aws_ec2.CfnInstance:
        """ Creates a single EC2 instance """
        security_group_ids = instance_config['security_group_ids']
        del instance_config['security_group_ids']

        return aws_ec2.CfnInstance(self, f'{instance_id}-instance', user_data=base64_message, **{
            **instance_config,
            'subnet_id': subnet.ref,
            'security_group_ids': [
                self.security_group_id_to_group_map[security_group_id].ref
                for security_group_id in security_group_ids
            ],
        })
