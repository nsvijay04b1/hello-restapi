/*variable "access_key" {
}

variable "secret_key" {
}
*/
variable "region" {
default ="us-east-1"
}

variable "key_name" {
default="hello-useast1-KP"
}

variable "s3_bucket" {
default="testbucket172.0.2.16"
}

variable "iam_instance_profile" {
default="EC2roleS3FullAccess"
}

variable "server_port" {
  description = "The port the server will use for HTTP requests"
  default     = 80
}

variable "ssh_port" {
  default = 22
}

variable "Count" {
  description = "Number of EC2 instances"
  default     = 1
}

