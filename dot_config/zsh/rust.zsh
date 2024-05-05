CARGO_HOME="${HOME}/.local/share/cargo"

if [ -d "${CARGO_HOME}" ]; then
  export CARGO_HOME

  source "${CARGO_HOME}/env"
fi

RUSTUP_HOME="${HOME}/.local/share/rustup"

if [ -d "${RUSTUP_HOME}" ]; then
  export RUSTUP_HOME
fi
