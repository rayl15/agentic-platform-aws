# Find the latest Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's owner ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Bastion instance
resource "aws_instance" "bastion" {
  ami                    = data.aws_ami.ubuntu.id  # Use Ubuntu instead of Amazon Linux
  instance_type          = "t3.large"
  subnet_id              = var.private_subnet_id
  vpc_security_group_ids = [aws_security_group.bastion_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.bastion_profile.name
  
  # Keep all your security settings
  ebs_optimized = true
  monitoring    = true
  
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  lifecycle {
     create_before_destroy = true
   }
  
  # Updated user data for Ubuntu with code-server and kubectl proxy
  user_data_replace_on_change = true
  user_data = <<-EOF
    #!/bin/bash
    
    # Update package lists
    apt-get update

    # Install build-essential, clang, and libomp-dev for c++ build of chromaDB.
    apt-get install -y build-essential clang libomp-dev
    
    # Install required packages
    apt-get install -y unzip curl jq git python3-pip python3-venv python3-dev

    # Install NVM
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

    # Install Node.js v23.9.0 (same as your laptop)
    nvm install 23.9.0
    nvm use 23.9.0
    nvm alias default 23.9.0

    # Make available system-wide
    ln -sf "$NVM_DIR/versions/node/v23.9.0/bin/node" /usr/local/bin/node
    ln -sf "$NVM_DIR/versions/node/v23.9.0/bin/npm" /usr/local/bin/npm
    ln -sf "$NVM_DIR/versions/node/v23.9.0/bin/npx" /usr/local/bin/npx

    # Verify
    /usr/local/bin/node --version

    # Set compiler environment variables in ubuntu user's profile
    cat >> /home/ubuntu/.profile << 'PROFILEEOF'
    # Set compiler environment variables for C++ builds
    export CC=clang
    export CXX=clang++
    export CFLAGS="-fPIC -O3"
    export CXXFLAGS="-fPIC -O3 -std=c++14"
    PROFILEEOF

    # Install Docker
    apt-get install -y docker.io
    # Allow ubuntu user to use docker without sudo
    usermod -aG docker ubuntu

    # Install Helm
    snap install helm --classic


    # Install kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    chmod +x kubectl
    mv kubectl /usr/local/bin/
    
    # Install AWS CLI v2
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
    
    # Configure kubectl for the EKS cluster as ubuntu user
    su - ubuntu -c "aws eks update-kubeconfig --name ${var.eks_cluster_name} --region ${data.aws_region.current.name}"
    
    # Install code-server (VS Code in the browser)
    su - ubuntu -c "curl -fsSL https://code-server.dev/install.sh | sh"

    # Install uv
    su - ubuntu -c "curl -LsSf https://astral.sh/uv/install.sh | sh"

    # Add uv environment to .bashrc for auto-loading
    su - ubuntu -c 'echo "source \$HOME/.local/bin/env" >> $HOME/.bashrc'
    

    # Git clone the sample repository
    su - ubuntu -c "git clone https://github.com/rayl15/agentic-platform-aws.git"
    # Create a simple script to run code-server and kubectl proxy
    cat > /home/ubuntu/start-code-server.sh << 'EOL'
    #!/bin/bash
    nohup code-server --port 8888 --auth none > /home/ubuntu/code-server.log 2>&1 &
    nohup kubectl proxy --port=8080 --address='0.0.0.0' --accept-hosts='.*' > /tmp/proxy.log 2>&1 &
    EOL
    
    chmod +x /home/ubuntu/start-code-server.sh
    chown ubuntu:ubuntu /home/ubuntu/start-code-server.sh
    
    # Auto-start code-server when system boots
    echo "@reboot ubuntu /home/ubuntu/start-code-server.sh" | tee -a /etc/crontab
    
    # Start code-server right away
    su - ubuntu -c "/home/ubuntu/start-code-server.sh"
  EOF

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}bastion-instance"
    }
  )
}
