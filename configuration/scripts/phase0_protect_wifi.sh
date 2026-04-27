#!/bin/bash
# phase0_protect_wifi.sh
# Run at the START of every SecureMac configuration session.
# Pins Claude API, GitHub, and Apple traffic to Wi-Fi (en1/cassinet)
# so network config changes cannot break the Claude Code connection.
#
# Usage: sudo bash ~/phase0_protect_wifi.sh

WIFI_GW="10.0.0.1"
WIFI_IF="en1"

echo "============================================================"
echo " Phase 0: Protecting Wi-Fi management path (cassinet/en1)"
echo " $(date)"
echo "============================================================"
echo ""

# Verify Wi-Fi is up
if ! ifconfig en1 | grep -q "inet "; then
  echo "ERROR: en1 (Wi-Fi) has no IP address. Connect to cassinet first."
  exit 1
fi

echo "Wi-Fi interface : $WIFI_IF"
echo "Wi-Fi gateway   : $WIFI_GW"
echo ""

# Pin Anthropic API
echo "-- Anthropic API (api.anthropic.com) --"
for IP in $(dig +short api.anthropic.com A 2>/dev/null | grep -E '^[0-9]'); do
  sudo route -q add -host "$IP" "$WIFI_GW" 2>/dev/null && echo "  Pinned $IP"
done

# Pin GitHub
echo "-- GitHub --"
for IP in $(dig +short github.com A 2>/dev/null | grep -E '^[0-9]'); do
  sudo route -q add -host "$IP" "$WIFI_GW" 2>/dev/null && echo "  Pinned $IP"
done

# Pin Apple CDN (software updates)
echo "-- Apple software updates --"
for IP in $(dig +short swscan.apple.com A 2>/dev/null | grep -E '^[0-9]'); do
  sudo route -q add -host "$IP" "$WIFI_GW" 2>/dev/null && echo "  Pinned $IP"
done

echo ""
echo "-- Verifying Claude API reachability via Wi-Fi --"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 --interface en1 https://api.anthropic.com/v1/messages 2>/dev/null)
echo "HTTP response: $HTTP"
if [ "$HTTP" = "401" ] || [ "$HTTP" = "405" ] || [ "$HTTP" = "200" ] || [ "$HTTP" = "403" ]; then
  echo "SUCCESS: Claude API reachable via cassinet Wi-Fi (en1)"
else
  echo "WARNING: Response $HTTP — verify Wi-Fi connection to cassinet"
fi

echo ""
echo "============================================================"
echo " Phase 0 complete. Safe to proceed with network config."
echo "============================================================"
