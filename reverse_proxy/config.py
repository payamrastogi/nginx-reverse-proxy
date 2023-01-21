from aws_cdk import aws_ec2

# basic VPC configs
VPC = 'rp-vpc'

INTERNET_GATEWAY = 'rp-internet-gateway'

KEY_PAIR_NAME = 'rp-us-east-1-key'

REGION = 'us-east-1'

# route tables
PUBLIC_ROUTE_TABLE = 'rp-public-route-table'

ROUTE_TABLES_ID_TO_ROUTES_MAP = {
    PUBLIC_ROUTE_TABLE: [
        {
            'destination_cidr_block': '0.0.0.0/0',
            'gateway_id': INTERNET_GATEWAY,
            'router_type': aws_ec2.RouterType.GATEWAY
        }
    ],
}

# security groups
SECURITY_GROUP = 'rp-sg'

SECURITY_GROUP_ID_TO_CONFIG = {
    SECURITY_GROUP: {
        'group_description': 'Security Group for reverse proxy',
        'group_name': SECURITY_GROUP,
        'security_group_ingress': [
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=80, to_port=80
            ),
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=80, to_port=80
            ),
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=443, to_port=443
            ),
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=443, to_port=443
            ),
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ip='0.0.0.0/0', from_port=22, to_port=22
            ),
            aws_ec2.CfnSecurityGroup.IngressProperty(
                ip_protocol='TCP', cidr_ipv6='::/0', from_port=22, to_port=22
            ),
        ],
        'tags': [{'key': 'Name', 'value': SECURITY_GROUP}]
    },
}

# subnets and instances
PUBLIC_SUBNET = 'rp-public-subnet'

PUBLIC_INSTANCE = 'rp-public-instance'

# AMI ID of the WordPress by Bitnami
AMI = 'ami-00874d747dde814fa'

SUBNET_CONFIGURATION = {
    PUBLIC_SUBNET: {
        'availability_zone': 'us-east-1a',
        'cidr_block': '10.0.1.0/24',
        'map_public_ip_on_launch': True,
        'route_table_id': PUBLIC_ROUTE_TABLE,
        'instances': {
            PUBLIC_INSTANCE: {
                'disable_api_termination': False,
                'key_name': KEY_PAIR_NAME,
                'image_id': AMI,
                'instance_type': 't2.micro',
                'security_group_ids': [SECURITY_GROUP],
                'tags': [
                    {'key': 'Name', 'value': PUBLIC_INSTANCE},
                ],
            },
        }
    },
}