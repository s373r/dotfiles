BUN_INSTALL="${HOME}/.local/share/bun"

if [ -d "${BUN_INSTALL}" ]; then
  export BUN_INSTALL
  export PATH="${BUN_INSTALL}/bin:${PATH}"

  source "${BUN_INSTALL}/_bun"
fi
