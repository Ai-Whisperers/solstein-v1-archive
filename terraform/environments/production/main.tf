terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket         = "solstein-terraform-state"
    key            = "environments/production/terraform.tfstate"
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

  environment = "production"
  aws_region  = "us-east-1"

  vpc_cidr             = "10.0.0.0/16"
  availability_zones   = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  node_instance_types     = ["t3.large", "t3.xlarge"]
  node_group_desired_size = 3
  node_group_min_size     = 3
  node_group_max_size     = 20

  db_instance_class        = "db.r5.large"
  db_allocated_storage     = 100
  db_max_allocated_storage = 500

  redis_node_type = "cache.r5.large"

  domain_name = "solstein.app"
}
