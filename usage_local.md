Base usage for local development
Clone repo
cd to folder with project
run "docker build -t litellm-gateway:latest -f dockerfile ."
wait for build
run "docker run -d --name litellm-gateway --env-file .env -p 8080:8080 litellm-gateway:latest"
