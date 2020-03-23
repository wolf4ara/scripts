import yaml
import sys

CONFIG_PATH = sys.argv[1]
PROJECT_NAME = sys.argv[2]
PARAM = sys.argv[3]

data = open(CONFIG_PATH, "r")
HOST = yaml.safe_load(data)[PROJECT_NAME]

if "servers" in HOST:
  OUT=next(server[PARAM] for server in HOST["servers"]  if "app" in server['roles'] or "web" in server['roles'])
else:
  OUT=HOST[PARAM]
data.close()
print(OUT)
