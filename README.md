
# Tesla PowerWall2

This is a node server to pull data from a Tesla Powerwall2 installation and make it available to a [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)

(c) 2020 Robert Paauwe
MIT license.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. Configure the node server per configuration section below.

### Node Settings
The settings for this node are:

#### Short Poll
   * How often to poll the PowerWall gateway (in seconds).

#### Long Poll
   * Not currently used.

#### IP Address
   * Tesla Powerwall gateway IP address

#### Serial Number
   * Tesla Powerwall gateway serial number

#### Password
   * Tesla Powerwall gateway password

## Node substitution variables
### Powerwall gateway node
 * sys.node.[address].ST      (Node sever online)
 * sys.node.[address].GV8     (Current mode of operation)
 * sys.node.[address].GV9     (Grid status)
 * sys.node.[address].BATLVL  (Battery status)

### Powerwall meter nodes
 * sys.node.[address].CPW     (Instant power)
 * sys.node.[address].GV0     (Instant reactive power)
 * sys.node.[address].GV1     (Instant apparent power)
 * sys.node.[address].GV2     (Frequency)
 * sys.node.[address].GV3     (Energy exported)
 * sys.node.[address].GV4     (Energy imported)
 * sys.node.[address].CV      (Instant average voltage)
 * sys.node.[address].CC      (Instant total current)
 * sys.node.[address].GV5     (i a current)
 * sys.node.[address].GV6     (i b current)
 * sys.node.[address].GV7     (i c current)

## Requirements
1. Polyglot V2.
2. ISY firmware 5.0.x or later
3. A Tesla Powerwall2

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "PowerWall".

Then restart the Powerwall nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes

- 1.0.0 06/02/2020
   - Initial version published to github for testing
