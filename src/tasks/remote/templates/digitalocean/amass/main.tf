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

resource "digitalocean_droplet" "task-amass" {
  depends_on = [tls_private_key.temp_pvt_key]

  image = "ubuntu-18-04-x64"
  name = "task-amass"
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
    source = "/usr/share/amass/config.ini"
    destination = "/tmp/config.ini"
  }

  provisioner "file" {
    source = "/home/d3d/.ssh/terraform_rsa.pub"
    destination = "/tmp/key.pub"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "apt-get update && apt-get upgrade -y",
      "apt-get -y install unzip",
      "mkdir -p /usr/share/amass",
      "cat /tmp/key.pub >> /root/.ssh/authorized_keys",
      "mv /tmp/config.ini /usr/share/amass",
      "wget https://github.com/OWASP/Amass/releases/download/v3.10.3/amass_linux_amd64.zip -O /tmp/amass.zip",
      "unzip /tmp/amass.zip -d /tmp && cp /tmp/amass_linux_amd64/amass /usr/bin",
      "touch /tmp/task.complete"
    ]
  }
}

output "web_ipv4_address" {
  description = "List of IPv4 addresses of web Droplets"
  value       = digitalocean_droplet.task-amass.ipv4_address
}