FLYCTL_INSTALL="${HOME}/.local/share/fly"

if [ -d "${FLYCTL_INSTALL}" ]; then
  export FLYCTL_INSTALL

  export PATH="${FLYCTL_INSTALL}/bin:${PATH}"
fi
