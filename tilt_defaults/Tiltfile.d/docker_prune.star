"""Docker prune settings."""

def set_docker_prune_defaults():
    docker_prune_settings(max_age_mins = 72 * 60, num_builds = 7, keep_recent = 3)
