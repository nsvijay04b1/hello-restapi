# Terraform to launch HA restapi on Ec2 isntances in a autoscaling group behind load balancer



Notice that you will need to create a terraform.tfvars yourself containing:
- access_key (AWS access key)
- secret_key (AWS secret key)
- region (AWS region)
- key_name (AWS SSH key)
- iam_instance_profile (AWS IAM profile for access to S3)
