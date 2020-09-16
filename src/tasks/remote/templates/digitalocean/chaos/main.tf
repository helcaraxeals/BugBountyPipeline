resource "random_string" "random" {
  length = 16
  special = false
}

resource "tls_private_key" "temp_pvt_key" {
  algorithm = "RSA"
  rsa_bits = 4096
}

resource "digitalocean_ssh_key" "ssh_key" {
  name = random_string.random.result
  public_key = tls_private_key.temp_pvt_key.public_key_openssh
}

resource "digitalocean_droplet" "task-chaos" {
  depends_on = [tls_private_key.temp_pvt_key]

  image = "ubuntu-18-04-x64"
  name = "task-chaos"
  region = "nyc3"
  size = "s-1vcpu-1gb"
  private_networking = true
  ssh_keys = [digitalocean_ssh_key.ssh_key.id]

  connection {
    host = self.ipv4_address
    user = "root"
    type = "ssh"
    private_key = tls_private_key.temp_pvt_key.private_key_pem
    timeout = "2m"
  }

  provisioner "file" {
    source = "/home/d3d/.ssh/terraform_rsa.pub"
    destination = "/tmp/key.pub"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "apt-get update && apt-get upgrade -y",
      "apt-get install golang -y",
      "GO111MODULE=on go get -u github.com/projectdiscovery/chaos-client/cmd/chaos",
      "cp ~/go/bin/chaos /usr/bin",
      "cat /tmp/key.pub >> /root/.ssh/authorized_keys",
      "touch /tmp/task.complete"
    ]
  }
}

output "web_ipv4_address" {
  description = "List of IPv4 addresses of web Droplets"
  value       = digitalocean_droplet.task-chaos.ipv4_address
}