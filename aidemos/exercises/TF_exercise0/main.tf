terraform {
  required_providers {
    awscc = {
      source  = "hashicorp/awscc"
      version = "~> 1.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "awscc" {
  region = "us-east-1" # Asegúrate que sea la región de tu lab
}

resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

resource "awscc_s3_bucket" "simple_bucket" {
  bucket_name = "fjmd-10052026-${random_integer.suffix.result}" # Solo minúsculas, números y guiones
}