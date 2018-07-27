
variable "cidr_admin_whitelist" {
  description = "CIDR ranges permitted to communicate with administrative endpoints"
  type        = "list"

  default = [
    "213.86.153.212/32",
    "213.86.153.213/32",
    "213.86.153.214/32",
    "213.86.153.235/32",
    "213.86.153.236/32",
    "213.86.153.237/32",
    "85.133.67.244/32",
  ]
}



resource "aws_security_group" "loadtest_group" {
  name        = "loadtest_group"
  description = "Load testing security group"

}

resource "aws_security_group_rule" "grafana_http" {
  type              = "ingress"
  to_port           = 3000
  from_port         = 3000
  protocol          = "tcp"
  security_group_id = "${aws_security_group.loadtest_group.id}"
  cidr_blocks       = ["${var.cidr_admin_whitelist}"]
}

resource "aws_security_group_rule" "prometheus_http" {
  type              = "ingress"
  to_port           = 9090
  from_port         = 9090
  protocol          = "tcp"
  security_group_id = "${aws_security_group.loadtest_group.id}"
  cidr_blocks       = ["${var.cidr_admin_whitelist}"]
}

resource "aws_security_group_rule" "instance_ssh" {
  type              = "ingress"
  to_port           = 22
  from_port         = 22
  protocol          = "tcp"
  security_group_id = "${aws_security_group.loadtest_group.id}"
  cidr_blocks       = ["${var.cidr_admin_whitelist}"]
}

resource "aws_security_group_rule" "locust_http" {
type              = "ingress"
to_port           = 8089
from_port         = 8089
protocol          = "tcp"
security_group_id = "${aws_security_group.loadtest_group.id}"
cidr_blocks       = ["${var.cidr_admin_whitelist}"]
}


resource "aws_security_group_rule" "egress_allow_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.loadtest_group.id}"
}

resource "aws_ebs_volume" "loadtest_disk" {
  availability_zone = "eu-west-1a"
  size = 10
  tags {
    Name = "Load testing disk"
  }
}


data "template_file" "user_data_script" {
  template = "${file("${path.module}/cloud.conf")}"
}


resource "aws_volume_attachment" "ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = "${aws_ebs_volume.loadtest_disk.id}"
  instance_id = "${aws_instance.loadtest_system.id}"

  depends_on = ["aws_ebs_volume.loadtest_disk"]
}

resource "aws_instance" "loadtest_system" {
  ami           = "ami-2a7d75c0"
  instance_type = "t2.small"
  availability_zone = "eu-west-1a"
  user_data = "${data.template_file.user_data_script.rendered}"

  security_groups = ["${aws_security_group.loadtest_group.name}"]
  key_name = "dj-test-jumpbox-key"
}

