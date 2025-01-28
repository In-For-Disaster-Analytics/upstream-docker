# upstream-docker

4 directories here:

- build: Dockerfile to build the container
- run: Example setup to run prod app & database
- run-dev: Example setup to run dev app & database. (so you can try stuff on this one first)
- traefik: the web proxy that will route web traffic to above containers 

## build

Build the docker container. Tag however you like (e.g. app:2). Note the name of the container so you can put it in docker-compose.yml

```
cd build 
docker build -t app:2 . 
```

## traefik

Traefik must be up to route to the apps. Copy to 

```
cp -r traefik ~/traefik
cd ~/traefik
```

Edit to your TLS certs and hostnames. 

Edit the lines in dynamic/tls.yml to reflect your host name.

Then burnup.

```
./burnup
```

## setup

The docker-compose and environment files will need to be configured beforey you can run. Recommend copying them out of this git repo to a place you can run them. e.g.

```
cp -r run ~/upstream-prod
cd ~/upstream-prod
```

Move `fastapi-env-example` to `fastapi-env` so you can edit.  Edit the lines in `fastapi-env` to reflect your environment.

Edit the line in docker-compose.yml to set your traefik Host.

Modify your docker-compose.yml to reflect location of fastapi-env.

Modify your docker-compose.yml to reflect location of your data volume(s). Recommend using a data dir next to the run dir and full path names, e.g. `/home/myusername/fastapi-data`

Edit other things probably. 


## run prod

To run the container and db behind the traefik proxy. Will end up at something like https://example.url/docs

```
cd ~/upstream-prod
```

start:

```
./burnup
```

stop:

```
./burndown
```

Data should not be lost between restarts if you retain your data dirs.


## run-dev

Follow the setup instructions for prod above, but use run-dev as the source config.

```
cp -r run-dev ~/upstream-dev
cd ~/upstream-dev
```

I made a close of the app and db apps for development purposes. You can run them completely separately and they won't interfere with the main app running at https://example.url/docs 

This runs at https://example.ur/dev/docs

For testing dev versions before deployment, just make sure you build and tag the image you want, e.g. 

(Wherever your build environment is:)
```
docker build -t app:dev-version-100 .
```

Edit docker-compose.yml to run the version of the image you just created.

```
  app-dev:
    container_name: app-dev
    image: app:dev-version-100
    ...
```

Up the app:

```
./burnup
```

