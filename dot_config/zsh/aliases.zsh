if command -v bat &> /dev/null; then
  alias cat='bat --paging=never'
  alias cat-orig='/usr/bin/cat'
fi
