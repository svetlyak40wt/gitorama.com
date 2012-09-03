Database schema
===============

Digest
------

Collection `received_events` stores user's activity stream
from the GitHub. Document structure the same is in the GitHub's API,
the only difference are `created_at` and `gitorama: {login: 'some-login'}`
fields.

Collection `daily_digests` stores aggregated data from the `received_events`.
Document's id is a user's login. Each digest has `repositories` list, sorted
by descended activity. In this list, each item has a `name`, `score` and
`events`, where `events` is a map of the standart GitHub's event names to
stripped information about event.
