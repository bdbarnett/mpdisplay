"""Local-only trees under ``lib/examples/`` — symlinks or gitignored checkouts.

Never included in ``packages/examples.json``, PyScript gallery generation, or CI.
"""

PERSONAL_EXAMPLE_DIRS = frozenset(
    {
        "frogger",
        "spotapi",
        "spotify_remote",  # pydevices sayso/apps/spotify_remote, if linked locally
        "spotify_client",  # alias if the symlink is renamed locally
    }
)
