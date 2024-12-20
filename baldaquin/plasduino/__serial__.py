# Copyright (C) 2024 the baldaquin team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import glob
import os

import baldaquin.plasduino.__boards__ as __boards__
from baldaquin import logger


AUTOCONFIG = 'automatic'


def scan_posix():
    """ Scan the tty ports and return a list of (port, vid, pid) tuples.
    """
    devices = []
    for folder in glob.glob('/sys/bus/usb/devices/*'):
        if not os.path.basename(folder).startswith('u') and ':' not in folder:
            vid = open(os.path.join(folder, 'idVendor')).read().strip()
            pid = open(os.path.join(folder, 'idProduct')).read().strip()
            vid = '0x%s' % vid
            pid = '0x%s' % pid
            ports = glob.glob('%s*:*/tty/*' % folder)
            if len(ports):
                port = ports[0]
            else:
                ports = glob.glob('%s*:*/tty*' % folder)
                if len(ports):
                    port = ports[0]
                else:
                    port = None
            if port is not None:
                port = os.path.join('/dev', os.path.basename(port))
            devices.append((folder, port, vid, pid))
    return devices


def autodetect_posix():
    """ Autodetect the first tty port with an arduino attached.
    """
    logger.info('Autodetecting arduino tty port...')
    for folder in glob.glob('/sys/bus/usb/devices/*'):
        if not os.path.basename(folder).startswith('u') and ':' not in folder:
            vid = open(os.path.join(folder, 'idVendor')).read().strip()
            pid = open(os.path.join(folder, 'idProduct')).read().strip()
            vid = '0x%s' % vid
            pid = '0x%s' % pid
            try:
                board = __boards__.SERIAL_ID_DICT[(vid, pid)]
                try:
                    port = glob.glob('%s*:*/tty/*' % folder)[0]
                except IndexError:
                    port = glob.glob('%s*:*/tty*' % folder)[0]
                port = os.path.join('/dev', os.path.basename(port))
                logger.info('Arduino %s found on port %s (vid %s, pid %s).' %\
                                (board, port, vid, pid))
                return (port, board, vid, pid)
            except KeyError:
                pass
    logger.info('No arduino found.')
    return (None, None, None, None)



def autodetect_nt():
    """ Autodetect the first serial port with an arduino attached.
    """
    try:
        import _winreg as winreg
    except ImportError:
        import winreg
    import itertools
    logger.info('Autodetecting arduino serial port...')
    try:
        handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r'HARDWARE\DEVICEMAP\SERIALCOMM')
    except WindowsError as e:
        abort(e)
    i = 0
    while 1:
        try:
            name, port, dummy = winreg.EnumValue(handle, i)
            usbSerNo = int(name.split('USBSER')[-1])
            h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'SYSTEM\CurrentControlSet\services\usbser\Enum')
            vid = pid = None
            # This could be done via regular expressions...
            for text in winreg.EnumValue(h, usbSerNo)[1].split('&'):
                if 'VID' in text:
                    vid = text.split('VID_')[-1][:4]
                    vid = '0x%s' % vid
                elif 'PID' in text:
                    pid = text.split('PID_')[-1][:4]
                    pid = '0x%s' % pid
            try:
                board = __boards__.SERIAL_ID_DICT[(vid, pid)]
                logger.info('Arduino %s found on port %s (vid %s, pid %s).' %\
                                (board, port, vid, pid))
                return (port, board, vid, pid)
            except KeyError:
                pass
            i += 1
        except WindowsError:
            break
    logger.info('No arduino found.')
    return (None, None, None, None)



def arduino_info(port = AUTOCONFIG, board = AUTOCONFIG):
    """ Return the port arduino is plugged into.
    """
    if port != AUTOCONFIG and board != AUTOCONFIG:
        vip = None
        pid = None
    elif os.name == 'posix':
        logger.info('Environmental variable $ARDUINO_PORT not set.')
        port, board, vip, pid = autodetect_posix()
    elif os.name == 'nt':
        logger.info('Environmental variable $ARDUINO_PORT not set.')
        port, board, vip, pid = autodetect_nt()
    return (port, board, vip, pid)



if __name__ == '__main__':
    print(arduino_info())
