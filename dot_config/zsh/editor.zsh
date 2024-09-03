if command -v rustrover &> /dev/null; then
  export EDITOR="rustrover --edit --wait"
else
  export EDITOR="nano"
fi
