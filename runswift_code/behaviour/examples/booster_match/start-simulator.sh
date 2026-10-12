#!/usr/bin/env bash
# Use the already provisioned, isolated Booster 1.10.5 container on marvin.
set -euo pipefail
container=runswift-world-model-sim
if [ "$(docker inspect --format '{{.HostConfig.NetworkMode}}' "$container")" = host ]; then
  echo 'Refusing a host-network simulator container.' >&2
  exit 1
fi
if [ "$(docker inspect --format '{{.State.Running}}' "$container")" = true ]; then
  echo 'Stop the existing simulator explicitly before starting the K1 scene.' >&2
  exit 1
fi
docker start "$container"
docker exec -d -e ROS_DOMAIN_ID=0 \
  -w /usr/local/booster_robot/booster_robocup_sim "$container" bash -c '
source /opt/ros/humble/setup.bash
source /opt/booster/BoosterRos2/install/setup.bash
export LD_LIBRARY_PATH=/opt/booster/Gait/lib:/opt/booster/Gait/lib/motion:$LD_LIBRARY_PATH
export PYTHONUNBUFFERED=1
exec .venv/bin/python app_in_container.py --model mjcf/football_pitch_4_K1.xml \
  --sim-transport ros --no-camera-relay --no-extension-process \
  > /tmp/runswift-match-simulator.log 2>&1
'
