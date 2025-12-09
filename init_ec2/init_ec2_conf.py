import paramiko
import time
from utils import helpers

class InitEC2:

    def __init__(self, config_file):
        """
        初始化 TidbOpConfig 类，加载配置文件并将其封装为类的属性。
        """
        self.config_file = config_file
        self.conf = self.set_conf()
        self.hosts = self.conf['host_list'].split(',')
        self.root_user = self.conf['root_user']
        self.root_password = self.conf['root_password']
        self.target_user = self.conf['target_user']
        self.target_password = self.conf['target_password']
        self.public_keys = {}
    
    def set_conf(self):
        self.conf = helpers.parse_yaml(self.config_file).get('initop')
        helpers.validate_non_empty_string(
            self.conf['host_list'],
            'initop.host_list',
            allow_none=False)
               
        return self.conf
    

    def ssh_connect(self, host):
        """建立 SSH 连接"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=self.root_user, password=self.root_password, timeout=10)
        return ssh

    def run_command(self, ssh, command):
        """执行命令并返回输出"""
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def setup_user(self, host):
        print(f"🔧 [{host}] 创建用户 {self.target_user} 并初始化环境")
        ssh = self.ssh_connect(host)

        commands = [
            f'id {self.target_user} || useradd -m {self.target_user}',
            f'echo "{self.target_user}:{self.target_password}" | chpasswd',
            f'mkdir -p /home/{self.target_user}/.ssh',
            f'chown -R {self.target_user}:{self.target_user} /home/{self.target_user}/.ssh',
            f'chmod 700 /home/{self.target_user}/.ssh',
            f'su - {self.target_user} -c "ssh-keygen -t rsa -f ~/.ssh/id_rsa -N \'\' -q"'
        ]
        for cmd in commands:
            self.run_command(ssh, cmd)

        ssh.close()

    def collect_public_key(self, host):
        print(f"📥 [{host}] 获取公钥")
        ssh = self.ssh_connect(host)
        sftp = ssh.open_sftp()
        pub_key_path = f"/home/{self.target_user}/.ssh/id_rsa.pub"
        with sftp.open(pub_key_path, 'r') as f:
            self.public_keys[host] = f.read().strip()
        ssh.close()

    def distribute_authorized_keys(self, host):
        print(f"📤 [{host}] 分发公钥 authorized_keys")
        all_keys = '\n'.join(self.public_keys.values())

        ssh = self.ssh_connect(host)
        sftp = ssh.open_sftp()
        temp_file = "/tmp/authorized_keys"

        # 写入所有公钥到临时文件
        with sftp.file(temp_file, 'w') as f:
            f.write(all_keys)
        sftp.chmod(temp_file, 0o644)

        # 移动到目标用户目录并设置权限
        cmds = [
            f"mv {temp_file} /home/{self.target_user}/.ssh/authorized_keys",
            f"chown {self.target_user}:{self.target_user} /home/{self.target_user}/.ssh/authorized_keys",
            f"chmod 600 /home/{self.target_user}/.ssh/authorized_keys"
        ]
        for cmd in cmds:
            self.run_command(ssh, cmd)

        ssh.close()

    def execute_all(self):
        # 1. 创建用户 & 生成密钥
        for host in self.hosts:
            self.setup_user(host)

        # 2. 收集公钥
        for host in self.hosts:
            self.collect_public_key(host)

        # 3. 分发公钥
        for host in self.hosts:
            self.distribute_authorized_keys(host)

        print("✅ 所有主机配置完成，用户已创建并实现互信登录。")