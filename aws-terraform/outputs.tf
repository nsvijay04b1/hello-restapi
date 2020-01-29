# Display ELB IP address
/*
output "alb_dns_name" {
  value = aws_alb.hello-alb.dns_name
}
*/
output "this_lb_dns_name" {
  description = "The DNS name of the load balancer."
  value       = concat(aws_lb.hello-alb.*.dns_name, [""])[0]
}

/*
output "ip" {
  value = aws_eip.ip.public_ip
}*/

/*
output "public_ips" {
  description = "List of public IP addresses assigned to the instances, if applicable"
  value       = aws_instances.getIp.public_ips
}
*/

