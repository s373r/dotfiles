if command -v docker &> /dev/null; then
  alias dive="docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive"
fi
