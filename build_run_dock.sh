#!/bin/bash
git pull

tag_name=$(cat src/VERSION.TXT)
data_folder=$(pwd)/data
log_folder=$(pwd)/logging
docker_name="telegram-bot${tag_name}"
image_name="python:3.11.0-slim-buster"

PS3='Build for (Ocean Server/Raspberry Server)?: '
server_options=("Ocean Server" "Raspberry Server")
select server in "${server_options[@]}"
do
    case $server in
        "Ocean Server")
            dockerfile="Dockerfile"
            image_name="python:3.11.0-slim-buster"
            break
            ;;
        "Raspberry Server")
            dockerfile="Dockerraspfile"
            image_name="python:3.11-slim-bookworm"
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

PS3='Build What?: '
# options=("dev" "acc" "prod" "Quit")
options=("acc" "prod" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "dev")
            echo "your choice is DEV"
            break
            ;;
        "prod")
            echo "your choice is PROD"
            break
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

docker build -f "$dockerfile" -t "$docker_name" .

docker run -it -d --network="host" -v "$log_folder:/src/logging" -e "TZ=Europe/Amsterdam" --log-opt tag="$docker_name/$image_name" --name="$docker_name" "$docker_name"

docker ps -a
