import socket

PORT = 5000

class currentMode() :
	def __init__(self, myenv):
		# mychain, myenv --> environment variables set in gunicornconf.py or manually if main.py is launched without Gunicorn
		self.admin = 'thierry.thevenet@talao.io'
		self.test = True
		self.myenv = myenv
		self.ipfs_gateway = 'https://talao.mypinata.cloud/ipfs/'
		self.deeplink = 'https://app.talao.co/'		
		if self.myenv == 'aws':
			self.sys_path = '/home/admin'
		else :
			self.sys_path = '/home/thierry'

		self.help_path = self.sys_path + '/Talao/templates/'
		self.uploads_path = self.sys_path + '/Talao/uploads/'

		# En Prod chez AWS 
		if self.myenv == 'aws':
			self.server = 'https://talao.co/'
			self.IP = '18.190.21.227' 

		elif self.myenv == 'local' :
			self.server = 'http://' + extract_ip() + ':' + str(PORT) +'/'
			self.IP = extract_ip()
			self.port = PORT
			print('mode.server = ', self.server)

		else :
			print('environment variable problem')
			exit()


def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP