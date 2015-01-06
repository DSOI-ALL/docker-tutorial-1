docker-tutorial-1
=================

Run a simple python web service in a docker container linking to database running in another container.

###Demo

Begin by starting in the `myapp` directory we created earlier on the virtual machine.  The rest of the tutorial will assume you are using, and on the command-line of the Vagrant-generated virtual machine provided with our [source code](https://github.com/SLS-ALL/docker-tutorial-1).

	cd /vagrant/myapp

1. Run the mongo container, using the official mongoDB docker image.  This will take a moment to pull the necessary layers from the repository.

		$ docker run --name mongo -d mongo
		
	The Docker `run` command starts a container.  In this instance we are starting a container named mongo (`--name mongo`).  You can name a container whatever you want.  The `-d` indicates to start the container in daemonized mode, or as a background process.  And finally, the second `mongo` is the name of the image to run.  If the image is not located locally it will attempt to pull an image named `mongo` from the Docker repository.
	
	To make sure it's working correctly, view the running docker containers by executing the `docker ps` command.

		$ docker ps

		CONTAINER ID    IMAGE        COMMAND                  CREATED         STATUS         PORTS       NAMES
		c1fc1ef13e1d    mongo:latest "/entrypoint.sh mongod   5 seconds ago   Up 5 seconds   27017/tcp   mongo


2. Build the python web service container. Make sure to include the trailing '.'

		$ docker build -t webservice .
	
	This command creates a docker container named `webservice` based on the `Dockerfile` in the current directory.

3. Run our web service container and link it to the running mongo container.  Expose port 8000 and make it available to our host.
  
	*Notice that we also want to mount our local source code, so we can make code
changes on the fly.  Use the full path of your **myapp** directory.*

		$ docker run --name webservice -p 8000:8000 -v /vagrant/myapp:/usr/src/app --link mongo:mongo -d webservice

4. Browse to *<http://localhost:8000/>* to initialize our data.
5. Browse to *<http:/localhost:8000/hello>* or *use the link on the web app home page* to see the data pulled from our mongo database container.

That's all there is to linking containers and using the environment variables
that are exposed to connect the containers together in an application.  

**But what if you want to actually get on the mongo console and see what is in your database?**

The docker way of doing this is to start up docker container based off of the existing mongo container an connect to your running instance.

There is no need to install the mongo client or shell tools on your own host or even guest OS.  The official mongo image we are using already has these tools, so we just need to need to start a new container and override it's entrypoint.  The only thing we need to know is the current IP Address of our running mongo container.  To get this address we inspect the container:

	$ docker inspect mongo

Near the bottom of the output we are looking for the *IPAddress* value in the *NetworkSettings* configuration.

	"NetworkSettings": {
        "Bridge": "docker0",
        "Gateway": "172.17.42.1",
        "IPAddress": "172.17.0.2",
        "IPPrefixLen": 16,
        "MacAddress": "02:42:ac:11:10:12",
        "PortMapping": null,
        "Ports": {
            "27017/tcp": null
        }
    }

In my case, the IP Address is ***172.17.0.2***.  So to start a mongo shell connecting to our mongo database we run the following:

	$ docker run -i -t --name "mongoshell" --entrypoint "mongo" mongo 172.17.0.2
	
<!-- -->

	MongoDB shell version: 2.6.6
	connecting to: 172.17.0.2/test
	Welcome to the MongoDB shell.
	For interactive help, type "help".
	For more comprehensive documentation, see
	http://docs.mongodb.org/
	Questions? Try the support group
	http://groups.google.com/group/mongodb-user
	>

We are now on the mongo shell of our mongo database.  You can now view the data we are creating when visiting <http://localhost:8000/> easily.  Our color
data is in the database named '**slsdb**' in the '**colors**' collection.

	> use slsdb
	switched to db slsdb
	> show collections
	colors
	system.indexes
	> db.colors.find()
	{ "_id" : ObjectId("5485eb8a3b65a90017ea338e"), "color" : "#7DE6B6" }
    { "_id" : ObjectId("5485ebd03b65a90017ea338f"), "color" : "#1C3160" }
    { "_id" : ObjectId("5485ecfb3b65a9001a39cdce"), "color" : "#C8618C" }
	{ "_id" : ObjectId("5485ee5d3b65a90026ff32d1"), "color" : "#973905" }
	{ "_id" : ObjectId("5485ee5f3b65a90026ff32d2"), "color" : "#06076A" }
	{ "_id" : ObjectId("5485ef643b65a9002fa9fcc6"), "color" : "#D5E272" }
	{ "_id" : ObjectId("5485ef823b65a9002fa9fcc7"), "color" : "#9B459E" }
	{ "_id" : ObjectId("5485ef863b65a9002fa9fcc8"), "color" : "#3C46EE" }


That's all for now. Have fun developing with Docker!
