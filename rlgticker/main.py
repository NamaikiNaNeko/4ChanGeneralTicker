import thread_updater
import memesign
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import textwrap

'''
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
'''


class AppServerSvc (win32serviceutil.ServiceFramework):
    """
    Used to create the appropriate windows service.
    """
    _svc_name_ = "mjg_ticker"
    _svc_display_name_ = "MJG Ticker"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.display = memesign.MemeSign()
        self.target_thread = thread_updater.ThreadMonitor('vg', ['mahjong', 'mjg'], 'F:/MJGTicker/lastpost.txt')
        self.timeout = 2000
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        """
        Handled on external stop request
        :return:
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """
        Starts the service. On start, log the appropriate message and then start doing self.main()
        :return: None
        """
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        """
        This holds the core functionality of the windows service. Tries to find the next post, and if available breaks
        it up into display-friendly string sizes and prints them. While waiting for string to complete or for a new
        post, also check for a stop request and break if necessary.
        :return:
        """
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        while True:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            post = self.target_thread.get_next_reply()
            if rc == win32event.WAIT_OBJECT_0:
                break
            if post is not None:
                splits = textwrap.wrap(post, 500)
                for i in range(len(splits)):
                    self.display.add_meme(splits[i])
                    while self.display.wait():
                        if rc == win32event.WAIT_OBJECT_0:  # In case a long message is being streamed, check during.
                            break
                    self.display.print_meme()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
