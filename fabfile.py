# -*- coding: utf-8 -*-
from fabric.api import *
import os
import time

#Use ssh configuration from ssh client configuration file
#env.use_ssh_config = True
#Or define env variables
#env.user = "vagrant"
#

#Variables
work_dir="automate_execution/"
downloads_dir = work_dir + "downloads/"
logs_dir = work_dir + "logs/"
results_dir = work_dir + "results/"
lynis_base_url = "http://cisofy.com/files/"
lynis_version_tar_file = "lynis-1.6.4.tar.gz"
lynis_version_dir = "lynis"



def prepare():
	#Prepare for executing with fab
	print 'Checking working directories'
	#Create base directories for execution
	local("mkdir -p " + work_dir)
	local("mkdir -p " + downloads_dir)
	local("mkdir -p "+logs_dir)
	local("mkdir -p "+results_dir)
	print 'Local directories checked'
	
def get_artfacts():
	#lynis
	with lcd(downloads_dir):
		local("wget " + lynis_base_url + lynis_version_tar_file)
		local("tar xfvz " + lynis_version_tar_file)


def rm_artfacts():
	local("rm -rf " + downloads_dir + "*")


def execute_remote_lynis():
	#Upload
	run("mkdir -p /tmp/testing/")
	run("mkdir -p /tmp/results/")
	put(downloads_dir+lynis_version_dir, "/tmp/testing")
	#Execute & store results
	sudo("chmod 640 -R /tmp/testing/"+lynis_version_dir)
	sudo("chmod u+x "+"/tmp/testing/"+lynis_version_dir+"/lynis")
	sudo("chown root:root -R /tmp/testing/"+lynis_version_dir)
	with cd("/tmp/testing/"+lynis_version_dir):
		sudo("./lynis --cron -c")
	#Download results
	sudo("chown " + env.user + " /var/log/lynis*")
	filelog = "lynis-"+env.host+"-"+time.strftime("%Y%m%d-%H%-M%S")+".log"
	filedat = "lynis-report-"+env.host+"-"+time.strftime("%Y%m%d-%H%-M%S")+".dat"
	run("cp /var/log/lynis.log /tmp/results/"+filelog)
	run("cp /var/log/lynis-report.dat /tmp/results/"+filedat)
	get("/tmp/results/lynis*",logs_dir)

def clean_remote():
	#Clean lynis remote
	run("rm -rf /tmp/results/")
	sudo("rm -rf /var/log/lynis*")
	sudo("rm -rf /tmp/testing")

def go():
	prepare()
	get_artfacts()
	execute_remote_lynis()
	clean_remote()
	rm_artfacts()


