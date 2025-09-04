from fabric import Connection, task
from invoke import Responder
import os
from pathlib import Path

# Configuration
REMOTE_HOST = "156.155.253.118"
REMOTE_USER = "deploy"
REMOTE_PATH = "/home/deploy/self-hosted-budget-ai-api"
REPO_URL = "https://github.com/eshaam/self-hosted-budget-ai-api"
SSH_KEY_PATH = "~/.ssh/id_rsa"  # Default SSH key path


@task
def deploy(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Deploy the application to the remote server"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        print("🚀 Starting deployment...")

        # Create directory if it doesn't exist
        conn.run(f"mkdir -p {REMOTE_PATH}")

        # Navigate to project directory
        with conn.cd(REMOTE_PATH):
            # Pull latest code
            print("📥 Pulling latest code...")
            try:
                conn.run("git pull origin master")
            except:
                print("🔄 Cloning repository...")
                conn.run(f"git clone {REPO_URL}.git .")

            # Backend deployment
            print("🐍 Setting up Python backend...")
            with conn.cd("backend"):
                # Create virtual environment if it doesn't exist
                conn.run("python3 -m venv venv || true")

                # Install dependencies with timeout and better options
                conn.run("venv/bin/pip install --upgrade pip")
                conn.run("venv/bin/pip install -r requirements.txt --timeout 300 --no-cache-dir")

                # Create necessary directories
                conn.run("mkdir -p config models logs")

                # Copy environment file if it doesn't exist
                result = conn.run("test -f .env", warn=True)
                if result.failed:
                    conn.run("cp .env.example .env")
                    print("⚠️  Please update .env file with production settings")

            # Frontend deployment
            print("⚛️  Building React frontend...")
            with conn.cd("frontend"):
                # Install Node.js dependencies
                conn.run("npm install")

                # Build for production
                conn.run("npm run build")

            # Restart services
            print("🔄 Restarting services...")
            restart_services(conn)

        print("✅ Deployment completed successfully!")


@task
def setup(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH, sudo_pass=None):
    """Initial server setup"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    
    # Configure sudo settings
    sudo_config = {}
    if sudo_pass:
        sudo_config["password"] = sudo_pass
    
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        # Set sudo configuration on the connection
        conn.config.sudo.password = sudo_pass if sudo_pass else None
        print("🛠️  Setting up server...")

        # Update system packages
       # conn.sudo("apt update && apt upgrade -y")

        # Install required packages
        # conn.sudo(
        #     "apt install -y python3 python3-pip python3-venv nodejs npm nginx git")

        # Install PM2 for process management
        conn.sudo("npm install -g pm2")

        # Create application directory
        conn.sudo(f"mkdir -p {REMOTE_PATH}")
        conn.sudo(f"chown {user}:{user} {REMOTE_PATH}")

        print("✅ Server setup completed!")


@task
def download_model(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Download the AI model to the remote server"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        print("🤖 Downloading AI model...")
        
        with conn.cd(f"{REMOTE_PATH}/backend"):
            # Create models directory if it doesn't exist
            conn.run("mkdir -p models")
            
            # Download the model using Python script
            print("📦 Downloading Qwen2-0.5B-Instruct model...")
            conn.run("venv/bin/python -c \"from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('Qwen/Qwen2-0.5B-Instruct'); AutoModelForCausalLM.from_pretrained('Qwen/Qwen2-0.5B-Instruct')\"")
            
        print("✅ Model download completed!")


def setup_nginx(conn):
    """Setup nginx configuration"""
    nginx_config = f"""
server {{
    listen 80;
    server_name self-hosted-budget-ai-api.eshaam.co.za;
    
    # Frontend
    location / {{
        root {REMOTE_PATH}/frontend/dist;
        try_files $uri $uri/ /index.html;
    }}
    
    # Backend API
    location /api {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""

    # Write nginx config
    conn.put(
        local=f"/tmp/self-hosted-budget-ai-api.conf",
        remote="/tmp/self-hosted-budget-ai-api.conf"
    )

    # Create the config file
    with open("/tmp/self-hosted-budget-ai-api.conf", "w") as f:
        f.write(nginx_config)

    conn.sudo("mv /tmp/self-hosted-budget-ai-api.conf /etc/nginx/sites-available/")
    conn.sudo(
        "ln -sf /etc/nginx/sites-available/self-hosted-budget-ai-api.conf /etc/nginx/sites-enabled/")
    conn.sudo("nginx -t && systemctl reload nginx")


@task
def restart_services(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Restart application services"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        restart_services(conn)


def restart_services(conn):
    """Helper function to restart services"""
    with conn.cd(f"{REMOTE_PATH}/backend"):
        # Stop existing processes
        conn.run("pm2 delete budget-ai-api || true", warn=True)

        # Start the application
        conn.run("pm2 start 'venv/bin/python -m app.main' --name budget-ai-api")

        # Save PM2 configuration
        conn.run("pm2 save")
        conn.run("pm2 startup || true", warn=True)


@task
def logs(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """View application logs"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        conn.run("pm2 logs budget-ai-api")


@task
def status(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Check application status"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        conn.run("pm2 status")


@task
def rollback(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Rollback to previous version"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        with conn.cd(REMOTE_PATH):
            conn.run("git reset --hard HEAD~1")
            restart_services(conn)
        print("🔄 Rolled back to previous version")


@task
def backup_config(c, host=REMOTE_HOST, user=REMOTE_USER, key_path=SSH_KEY_PATH):
    """Backup configuration files"""
    connect_kwargs = {"key_filename": os.path.expanduser(key_path)}
    with Connection(f"{user}@{host}", connect_kwargs=connect_kwargs) as conn:
        timestamp = conn.run("date +%Y%m%d_%H%M%S", hide=True).stdout.strip()
        backup_dir = f"/tmp/backup_{timestamp}"

        conn.run(f"mkdir -p {backup_dir}")
        conn.run(f"cp -r {REMOTE_PATH}/backend/config {backup_dir}/")
        conn.run(
            f"tar -czf backup_{timestamp}.tar.gz -C /tmp backup_{timestamp}")

        print(f"📦 Backup created: backup_{timestamp}.tar.gz")
