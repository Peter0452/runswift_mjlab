# Sources

One record per original source of an approach: a paper, a repository, or our
own work. A source describes *their* task and setting and their approach as a
combination of elements (agent, reward, value, model, environment,
optimisation), so a relevant paper translates directly into a candidate task
implementation. What we took from it, where and with what result is in the use
records (`knowledge/uses/`); the approach cards link back here.

(`knowledge/sources.md`, without the `s/`, is a different thing: the index of
our original notes the knowledge base was built from.)

`<id>.md`: YAML front matter, then a short body.

| Field | Meaning |
|---|---|
| `id` | `author<year>_<short>` for papers, a short name for repositories, `ours` |
| `kind` | `paper`, `repo` or `ours` |
| `title`, `citation`, `url`, `path`, `licence` | where to find it (local clones are siblings of `runswift_mjlab/`) |
| `task`, `robot` | their setting: how far their evidence transfers to the K1 |
| `approach` | their approach as elements: a list of `{element, what}` |
| `approaches` | our cards that came from it |
| `extraction` | `not read`, `summary`, `extracted` (approach atoms), `claims` (claims and numbers recorded) |
| `notes` | anything else (licence caveats, how it reached us) |

A literature review (`knowledge/reviews/`) adds or deepens source records; a
paper's claims never change an approach's status (only uses do).
