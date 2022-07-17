provider "google" {
  project     = var.project_name
  region      = "europe-west1"
  zone        = "europe-west1-d"
  credentials = file(var.path_to_gcp_key)
}


resource "google_compute_network" "vpc_network" {
  name = var.project_vpc
}

resource "google_compute_firewall" "vpc_firewall_ssh" {
  name          = "main-network-ssh"
  network       = google_compute_network.vpc_network.name
  description   = "Firewall rules that apply to the main node."
  target_tags   = ["jenkins"]
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "vpc_firewall_icmp" {
  name          = "main-network-icmp"
  network       = google_compute_network.vpc_network.name
  description   = "Firewall rules that apply to the main node."
  target_tags   = ["jenkins"]
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "icmp"
  }
}

resource "google_compute_firewall" "vpc_firewall_http" {
  name          = "main-network-http"
  network       = google_compute_network.vpc_network.name
  description   = "Firewall rules that apply to the main node."
  target_tags   = ["jenkins"]
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["80", "443"] // http-01 challenge
  }
}

resource "google_compute_firewall" "vpc_firewall_jenkins" {
  name          = "main-network-jenkins"
  network       = google_compute_network.vpc_network.name
  description   = "Firewall rules that apply to the main node."
  target_tags   = ["jenkins"]
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports    = ["8443"] // jenkins
  }
}

resource "google_compute_instance" "main-node" {
  name         = "jenkins-main-tf"
  machine_type = var.main_node_type
  zone         = "us-central1-c"
  tags         = ["jenkins"]

  boot_disk {
    initialize_params {
      image = var.main_node_image
      size  = var.main_node_disk_size
      type  = "pd-standard"
    }
  }

  metadata = {
    ssh-keys = "${var.main_node_ssh_username}:${file(var.path_main_node_ssh_pubkey)}"
}

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      nat_ip = var.main_node_IP
    }
  }

  provisioner "remote-exec" {
    inline = [
      "echo 'Ssh connection established. Proceeding to remote configuration.'"
    ]
    connection {
      type        = "ssh"
      user        = "ansible"
      host        = var.main_node_IP
      port        = 22
      private_key = file(var.path_main_node_ssh_key)
    }
  }

  provisioner "local-exec" {
    command = <<-EOT
            sed -i /^${var.main_node_IP}/d ~/.ssh/known_hosts

            echo    "[main_jenkins_node]"                                                    >  /tmp/hosts.txt
            echo -n "instance1 ansible_host=${var.main_node_IP} "                            >> /tmp/hosts.txt
            echo -n "ansible_user=ansible ansible_ssh_private_key_file=./main-node.ssh.key " >> /tmp/hosts.txt
            echo -n "docker_listen_address=tcp://127.0.0.1:4243 "                            >> /tmp/hosts.txt
            echo -n "jenkins_domain=jenkins-tf.rrops.pp.ua"                                  >> /tmp/hosts.txt
            echo -n "jenkins_pkcs12=keys.pkcs12"                                             >> /tmp/hosts.txt
            echo -n "jenkins_jks=/var/lib/jenkins/keys.jks"                                  >> /tmp/hosts.txt
            echo -n "jenkins_https_port=8443"                                                >> /tmp/hosts.txt
            echo -n "jenkins_keystore_password=${var.keystore_password}"                     >> /tmp/hosts.txt

            ansible-playbook --version
            ANSIBLE_HOST_KEY_CHECKING=False ANSIBLE_CONFIG=./ansible.cfg ansible-playbook -i /tmp/hosts.txt ./jenkins-setup.yaml
            rm -fv /tmp/hosts.txt

            mv ./password_jenkins-tf.rrops.pp.ua/instance1/var/lib/jenkins/secrets/initialAdminPassword ./jenkins_init_pass.txt
            rm -rfv ./password_jenkins-tf.rrops.pp.ua/
            printf "Use this to log into https://jenkins-tf.rrops.pp.ua:8443\n> %s\n" $(cat ./jenkins_init_pass.txt)
        EOT
  }
}

resource "google_container_cluster" "production-cluster" {
  name                     = "tg-ytdlp-bot-cluster"
  location                 = "europe-west1"
  network                  = google_compute_network.vpc_network.name
  remove_default_node_pool = true
  initial_node_count       = 1

  addons_config {
    horizontal_pod_autoscaling {
      disabled = true
    }
  }
}

resource "google_container_node_pool" "production-pool" {
  name       = "main-pool"
  location   = "europe-west1"
  cluster    = google_container_cluster.production-cluster.name
  node_count = 1

  node_config {
    preemptible  = true
    disk_size_gb = 10
    disk_type    = "pd-standard"
    machine_type = "e2-micro"
  }
}
