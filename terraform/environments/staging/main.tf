terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "solstein-terraform-state"
    key            = "environments/staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "solstein-terraform-locks"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "infrastructure" {
  source = "../../modules/infrastructure"

  environment = "staging"
  aws_region  = "us-east-1"

  vpc_cidr             = "10.1.0.0/16"
  availability_zones   = ["us-east-1a", "us-east-1b"]
  private_subnet_cidrs = ["10.1.1.0/24", "10.1.2.0/24"]
  public_subnet_cidrs  = ["10.1.101.0/24", "10.1.102.0/24"]

  node_instance_types     = ["t3.medium"]
  node_group_desired_size = 2
  node_group_min_size     = 1
  node_group_max_size     = 5

  db_instance_class        = "db.t3.medium"
  db_allocated_storage     = 20
  db_max_allocated_storage = 100

  redis_node_type = "cache.t3.micro"

  domain_name = "staging.solstein.app"
}
