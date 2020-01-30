#---------------------------------#
#  #
#                                 #
# Deploys two highly available RESTAPI servers to AWS   #
#---------------------------------#

# Configure AWS connection, secrets are in terraform.tfvars
provider "aws" {
  shared_credentials_file = "~/.aws/creds"
  #access_key = var.access_key
  #secret_key = var.secret_key
  region     = var.region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "all" {
  vpc_id = data.aws_vpc.default.id
}

data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.default.id
  name   = "default"
}


module "db" {
  source = "./modules/db"

  identifier = "demodb"

  engine            = "postgres"
  engine_version    = "9.6.3"
  major_engine_version = "9.6"
  instance_class    = "db.t2.micro"
  allocated_storage = 5
  storage_encrypted = false

  # kms_key_id        = "arm:aws:kms:<region>:<accound id>:key/<kms key id>"
  name = "demodb"

  # NOTE: Do NOT use 'user' as the value for 'username' as it throws:
  # "Error creating DB Instance: InvalidParameterValue: MasterUsername
  # user cannot be used as it is a reserved word used by the engine"
  username = "demouser"
  password = "demouser123"
  port     = "5432"
  vpc_security_group_ids = [data.aws_security_group.default.id]
  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"
  # disable backups to create DB faster
  backup_retention_period = 0
  tags = {
    Owner       = "user"
    Environment = "dev"
  }
  # DB subnet group
  subnet_ids = data.aws_subnet_ids.all.ids
  # DB parameter group
  family = "postgres9.6"
  # Snapshot name upon DB deletion
  #final_snapshot_identifier = "demodb"  nosnapshot needed
  skip_final_snapshot  = true


}

# Get availability zones for the region specified in var.region
data "aws_availability_zones" "all" {
}

# Create autoscaling policy -> target at a 70% average CPU load
resource "aws_autoscaling_policy" "hello-asg-policy-1" {
  name                   = "hello-asg-policy"
  policy_type            = "TargetTrackingScaling"
  adjustment_type        = "ChangeInCapacity"
  autoscaling_group_name = aws_autoscaling_group.hello-asg.name

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 70
  }
}

# Create an autoscaling group
resource "aws_autoscaling_group" "hello-asg" {
  name                 = "hello-asg"
  launch_configuration = aws_launch_configuration.hello-lc.id
  availability_zones   = data.aws_availability_zones.all.names
  health_check_grace_period = 600
  default_cooldown          = 600
  min_size = 2
  max_size = 2

  #load_balancers    = [aws_lb.hello-alb.name]
  target_group_arns = [aws_lb_target_group.hello-tg.arn]
  health_check_type = "ELB"

  tag {
    key                 = "Name"
    value               = "hello-ASG"
    propagate_at_launch = true
  }
}

# Create launch configuration
resource "aws_launch_configuration" "hello-lc" {
  name            = "hello-lc"
  image_id        = "ami-0c322300a1dd5dc79"
  instance_type   = "t2.micro"
  key_name        = var.key_name
  security_groups = [aws_security_group.hello-lc-sg.id]

  iam_instance_profile = var.iam_instance_profile

  user_data = <<-EOF
#!/bin/bash
sudo sudo yum update -y
sudo yum install nginx python2 python2-pip git python2-psycopg2 -y
sudo python2 -m pip install awscli gunicorn flask
sudo git clone https://github.com/nsvijay04b1/hello-restapi.git /app
sudo aws s3 cp "s3://${var.s3_bucket}/helloapp.service" /etc/systemd/system/helloapp.service
sudo systemctl enable helloapp
sudo systemctl start helloapp
sudo aws s3 cp "s3://${var.s3_bucket}/nginx.conf" /etc/nginx/nginx.conf
sudo systemctl enable nginx
sudo systemctl start nginx
EOF


  lifecycle {
    create_before_destroy = true
  }
}


# Create the ELB

resource "aws_lb" "hello-alb" {
  name               = "hello-load-balancer"
  security_groups    = [aws_security_group.hello-alb-sg.id]
  internal           = false
  load_balancer_type = "application"
  subnets            = data.aws_subnet_ids.all.ids
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.hello-alb.arn
  port              = "80"
  protocol          = "HTTP"
  #ssl_policy        = "ELBSecurityPolicy-2016-08"
  #certificate_arn   = "${var.certificate}"

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "Not Found"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_rule" "alb-nginx-heartbeat" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.hello-tg.arn
  }

  condition {
    path_pattern {
      values = ["/"]
    }
  }
}

resource "aws_lb_listener_rule" "alb-hello-api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 99 

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.hello-tg.arn
  }

  condition {
    path_pattern {
      values = ["/hello/*"]
    }
  }

}


resource "aws_lb_target_group" "hello-tg" {
  name        = "hello-alb-tg"
  target_type = "instance"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
}

# Create security group that's applied the launch configuration
resource "aws_security_group" "hello-lc-sg" {
  name = "hello-lc-sg"

  # Inbound HTTP from anywhere
  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = var.ssh_port
    to_port     = var.ssh_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create security group that's applied to the ELB
resource "aws_security_group" "hello-alb-sg" {
  name = "hello-alb-sg"

  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound HTTP from anywhere
  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }


}

/*provisioner "local-exec" {
   command  = "sed -e 's/HOST_DB/'${this_db_instance_endpoint}'/g' -i ../hello-app/database.ini ; psql -h  -d demodb -U demouser -W demouser123 -f ../hello-app/tests/testdata.txt "
}
*/

/*
sleep 30; ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v -i '${self.public_ip},' --key-file ../terr.pem ./ansible/config.yml -e 'ansible_python_interpreter=/usr/bin/python3'"

*/
/*
data "aws_instances" "getIp" {
  instance_tags = {
    tag = "Name"
    values = "hello-ASG"
  }

  filter {
    tag   = "Name"
    values = "hello-ASG"
  }

  instance_state_names = ["running" ]

  public_ips=["${network-interface.addresses.association.public-ip}"]

}
*/
