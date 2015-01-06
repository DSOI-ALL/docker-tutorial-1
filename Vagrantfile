# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

 config.vm.box = "slsdemo_docker1"
 config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

 config.vm.provider "virtualbox" do |v|
   v.memory = 2048 # set ram to 2gb, for speedier data ingestion
 end

 config.vm.network :forwarded_port, guest: 8000, host: 8000   # webapp
 config.vm.network :forwarded_port, guest: 27017, host: 27017 # mongodb

 # Issue command line commands to configure the Vagrant VM...

 # if docker isn't installed, install it
 if Dir.glob("#{File.dirname(__FILE__)}/.vagrant/machines/default/*/id").empty?
   # Install Docker
   pkg_cmd = "wget -q -O - https://get.docker.io/gpg | apt-key add -;" \
     "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list;" \
     "apt-get update -qq; apt-get install -q -y --force-yes lxc-docker; "
   # Add vagrant user to the docker group
   pkg_cmd << "usermod -a -G docker vagrant; "
   config.vm.provision :shell, :inline => pkg_cmd
 end

end
