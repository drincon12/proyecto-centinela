terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "aws_region" {
  description = "Región AWS para el entorno Centinela"
  type        = string
  default     = "us-east-1"
}

provider "aws" {
  region = var.aws_region
}

# VPC básica para Centinela
resource "aws_vpc" "centinela" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "centinela-vpc"
    Project = "Proyecto-Centinela"
    Environment = "staging"
  }
}

# Subred pública
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.centinela.id
  cidr_block              = "10.20.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "centinela-public-subnet"
    Project = "Proyecto-Centinela"
  }
}

# Security Group para la VM de Centinela
resource "aws_security_group" "centinela_sg" {
  name        = "centinela-sg"
  description = "Permitir HTTP/HTTPS para Centinela"
  vpc_id      = aws_vpc.centinela.id

  # SSH abierto a Internet (Checkov lo va a marcar como riesgo: sirve para el informe)
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Salida a Internet"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "centinela-sg"
    Project = "Proyecto-Centinela"
  }
}
