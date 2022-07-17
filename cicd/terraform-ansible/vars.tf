variable "project_name" {
  type        = string
  default     = "cicd-tg-ytdlp-bot"
  description = "Project name."
  nullable    = false
}

variable "project_vpc" {
  type        = string
  default     = "main-network"
  description = "Project's default VPC network."
  nullable    = false
}

variable "path_to_gcp_key" {
  type        = string
  default     = "./terraform-key.json"
  description = "Access key issued to the service account."
  nullable    = false
}

variable "main_node_type" {
  type        = string
  default     = "g1-small"
  description = "Instance type to run on."
  nullable    = false
}

variable "main_node_image" {
  type        = string
  default     = "debian-cloud/debian-11"
  description = "Family and image name of the host OS."
  nullable    = false
}

variable "main_node_disk_size" {
  type        = number
  default     = 15
  description = "Size of boot drive to boot from."
  nullable    = false

  validation {
    condition     = var.main_node_disk_size >= 10
    error_message = "Minimum disk size is 10."
  }
}

variable "main_node_IP" {
  type        = string
  default     = "34.70.49.7"
  description = "Public static IP address to access the instance over the Internet."
  nullable    = false
}

variable "main_node_ssh_username" {
  type        = string
  default     = "ansible"
  description = "Username used for logging in via ssh."
  nullable    = false
}

variable "path_main_node_ssh_key" {
  type        = string
  default     = "./main-node.ssh.key"
  description = "Ssh key used to log in to the main node."
  nullable    = false
}

variable "path_main_node_ssh_pubkey" {
  type        = string
  default     = "./main-node.ssh.key.pub"
  description = "Ssh key used to log in to the main node."
  nullable    = false
}

variable "keystore_password" {
    type = string
    description = "Password used to access jenkins keystore. Pass via envvars. (i.e. TF_VAR_keystore_password=<password>)"
    sensitive = true
}
