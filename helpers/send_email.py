import smtplib
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
import logging


signature = '\r\n\r\n\r\n\r\nThe Talao team.\r\nhttps://talao.io/'

""" Envoi du code secret """
def message(email_to, random, password) :

	# debut de la fonction
	fromaddr = "relay@talao.io"
	toaddr = [email_to, ]

	# instance of MIMEMultipart
	msg = MIMEMultipart()
	msg['From'] = formataddr((str(Header('Talao', 'utf-8')), fromaddr))
	msg['To'] = ", ".join(toaddr)
	msg['Subject'] = 'Talao : Email authentification  '

	# string to store the body of the mail
	body = 'Your verification code is : '+ random
	msg.attach(MIMEText(body, 'plain'))
	#p = MIMEBase('application', 'octet-stream')

	# creates SMTP session
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(fromaddr, password)
	text = msg.as_string()

	# sending the mail
	try:
		s.sendmail(msg['from'],  msg["To"].split(","), text)
		s.quit()
		return True
	except:
		logging.error('sending mail')
		s.quit()
		return False
	
