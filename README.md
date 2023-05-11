# device_control

**THIS REPOSITORY IS PUBLIC**
Mind before committing IP adresses, passwords, keys of any sort.
Adding third-party software is OK if it isn't confidential.

Confidential content should be in the **computer-config** (private) repository.
The latter includes scxconf, which contain IP macros.

For example, instead of hard-coding an IP here, use a name (as set by the `/etc/hosts` configuration in `computer-config` repo)

## Rationale

Why keep seven versions of CONEX driver code sitting around when it can be in one place?

## Installation

```
pip install -e .
```
