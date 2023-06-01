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
## Configuration

Note: in order to use the `VAMPIRESTrigger` you will need to set up device permissions for the inline USB switch. To do this, copy the `conf/vampires/99-ykushxs-usb.rules` file to `/etc/udev/rules.d/`
```
sudo cp conf/vampires/99-ykushxs-usb.rules /etc/udev/rules.d
```
or, if you prefer links
```
sudo ln -s conf/vampires/99-ykushxs-usb.rules /etc/udev/rules.d
```

Then, reload the `udev` daemon
```
sudo udevadm trigger
```