---
name: word_count
track: core
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [word_count, character_count]
side_effect: false
---
# word_count

Counts words and characters in a supplied text. It does not call external APIs
and does not modify files.
