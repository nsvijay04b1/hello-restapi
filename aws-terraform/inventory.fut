data "template_file" "inventory" {
    template = "${file("./inventory.tpl")}"

    vars {
       ec2.public.ip = public_ip
    }
}

resource "local_file" "save_inventory" {
  content  = "${data.template_file.inventory.rendered}"
  filename = "./myhost"
}
