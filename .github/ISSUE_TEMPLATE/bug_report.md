name: 🐛 Bug Report
description: Report something that is not working correctly
title: "[Bug] "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
        
        ## Describe the Bug
        A clear and concise description of what the bug is.
        
        ## To Reproduce
        Steps to reproduce the behavior:
        1. Go to '...'
        2. Run '...'
        3. See error
        
        ## Expected Behavior
        A clear description of what you expected to happen.
        
        ## Screenshots
        If applicable, add screenshots to help explain your problem.
        
        ## Environment:
        - OS: [e.g. macOS, Windows, Linux]
        - Python version: [e.g. 3.10, 3.11]
        - SoulForge version: [e.g. 0.1.0]
        
        ## Additional Context
        Add any other context about the problem here.
  - type: textarea
    id: bug
    attributes:
      label: Bug Description
      placeholder: Describe the bug...
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      placeholder: |
        1. First step
        2. Second step
        3. ...
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
    validations:
      required: true
