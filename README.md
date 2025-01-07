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

start:

```
./burnup
```

stop:

```
./burndown
```

Data should not be lost between restarts if you retain your data dirs.


