import subprocess
import time
import os

# Clean any existing vpnns
subprocess.run(['sudo', 'ip', 'netns', 'del', 'vpnns'], stderr=subprocess.DEVNULL)
subprocess.run(['sudo', 'ip', 'netns', 'add', 'vpnns'])

print("Netns vpnns created successfully.")
subprocess.run(['sudo', 'ip', 'netns', 'exec', 'vpnns', 'ip', 'link', 'set', 'lo', 'up'])

# Clean up
subprocess.run(['sudo', 'ip', 'netns', 'del', 'vpnns'])
print("Clean up ok.")
