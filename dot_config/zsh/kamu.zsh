if command -v kamu &> /dev/null; then
  # NOTE: Using bash is intentional
  # shellcheck disable=SC1090
  source <(kamu completions bash)
fi
