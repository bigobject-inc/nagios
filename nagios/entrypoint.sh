#!/bin/bash -e
    # setup timezone
    if [ -z "$TZ" ]; then
        echo "[WARNING] environment TZ is not set"
    fi
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone

    # verify configuration
    echo "[INFO] Verifying nagios configuration"
    /usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg

    # bootstrap
    htpasswd -cb /usr/local/nagios/etc/htpasswd.users nagiosadmin ${NAGIOS_PSWD:-nagios}
    chown -R nagios:nagios /opt/ssh

    # start all relating services
    service apache2 restart
    service nagios restart

    # if everything is OK
    echo "[INFO] Everything is OK"
    /bin/bash
