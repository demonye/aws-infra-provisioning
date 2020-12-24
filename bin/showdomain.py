#!/usr/bin/env python3

import boto3


if __name__ == '__main__':
    sts = boto3.client('sts')
    cf = boto3.client('cloudfront')
    region_name = sts.meta.region_name

    bucket_name = 'eric-devops-demo-web'
    resp = cf.list_distributions()
    bucket_domain_name = f"{bucket_name}.s3-website-{region_name}.amazonaws.com"
    founds = list(filter(
        lambda v: v['Origins']['Items'][0]['DomainName'] == bucket_domain_name,
        resp['DistributionList']['Items']
    ))
    distribution = founds and founds[0]
    domain_name = distribution['DomainName'] if 'DomainName' in distribution else None

    if domain_name:
        print(
            '\n\n\n\n'
            f'CloutFront domain: \033[1;31mhttp://{domain_name}\033[0m\n\n'
            'Open in browser to test the website.\n\n'
            'It might take up to 10 minutes to go live, take a break and come back later!\n'
            '\n\n\n\n'
        )
    else:
        print(
            '\n\n\n\n\n'
            'Not table to get the domain name!\n'
            'Contact administrator to fix.'
            '\n\n\n\n\n'
        )
