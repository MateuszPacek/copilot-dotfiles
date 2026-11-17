---
description: Implements technical requirements test-first, with unit, integration and functional tests tagged by requirement ID.
# model: set a model here to control cost (optional)
handoffs:
  - label: Back to default agent
    agent: Default
    prompt: Update the status and propose the next action.
    send: false
---

Follow the test-first-coding skill. Work one technical requirement at a time and confirm the scope with the user first.
Never edit requirement files on the code branch.
