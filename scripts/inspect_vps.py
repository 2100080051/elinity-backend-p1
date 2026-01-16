import paramiko
import sys

host = "168.231.112.236"
user = "root"
password = "Elinity@Deckoviz1"

def run_remote_command(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, key_filename=r"C:\Users\nabhi\.ssh\id_ed25519")
        
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        ssh.close()
        return output, error
    except paramiko.BadAuthenticationType as e:
        return None, f"Bad Auth Type. Allowed: {e.allowed_types}"
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    print(f">>> Inspecting VPS: {host}")
    
    commands = [
        "uptime",
        "docker ps",
        "ls -la /root",
        "netstat -tuln | grep LISTEN"
    ]
    
    for cmd in commands:
        print(f"\n>>> Running: {cmd}")
        out, err = run_remote_command(cmd)
        if out:
            print(out)
        if err:
            print(f"Error: {err}")
