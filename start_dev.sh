# NAME=gradio-aggregator
# docker build --platform linux/amd64  -t $NAME .
# docker stop $NAME
# sleep 5

# docker run -d \
#   --rm \
#   --name $NAME \
#   --platform linux/amd64 \
#   -v $(pwd)/src:/src \
#   -v $(pwd)/../volume:/volume \
#   -p 8000:8000 \
#   -p 8888:8888 \
#   $NAME \
#   sleep infinity

docker compose up --build