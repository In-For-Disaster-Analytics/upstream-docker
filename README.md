# upstream-docker
 

## build

```
cd build 
docker build -t app:2 . 
```

## config

Copy the run directory somewhere outside the git repo so you can edit things. e.g.:

```
cp -r run ~/tmp
cd ~/tmp/run
```

Move `fastapi-env-example` to `fastapi-env` so you can edit.

Edit the lines in it to reflect your environment.

Edit the line in docker-compose.yml to set your traefik Host.

Edit the lines in dynamic/tls.yml to reflect your host name.

Modify your docker-compose.yml to reflect location of fastapi-env.

Modify your docker-compose.yml to reflect location of your data volume(s). Recommend using a data dir next to the run dir and full path names, e.g. `/home/myusername/fastapi-data`



Edit other things probably. 


## run

To run the container and db behind the traefik proxy. Will end up at something like https://example.url/docs


```
cd run
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

```
cd run-dev
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

