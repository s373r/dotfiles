editor() {
  if command -v rustrover &> /dev/null; then
    rustrover --edit --wait "$@"
  else
    nano "$@"
  fi
}

export EDITOR=editor
