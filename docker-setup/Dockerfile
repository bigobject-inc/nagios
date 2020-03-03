FROM ubuntu:16.04

# Part 1. install required packages
RUN sed -i s/http/ftp/ /etc/apt/sources.list \
    # fix apt repository failure
    
    && echo postfix postfix/main_mailer_type string "'Internet Site'" | debconf-set-selections \  
    && echo postfix postfix/mynetworks string "127.0.0.0/8" | debconf-set-selections \
    && echo postfix postfix/mailname string nagios.example.com | debconf-set-selections \
    && export DEBIAN_FRONTEND="noninteractive" \
    && apt-get update \
    && apt-get install -y apache2 apache2-utils autoconf automake bc bsd-mailx build-essential dnsutils fping gettext git gperf iputils-ping jq libapache2-mod-php libcache-memcached-perl libcgi-pm-perl libdbd-mysql-perl libdbi-dev libdbi-perl libfreeradius-client-dev libgd2-xpm-dev libgd-gd2-perl libjson-perl libldap2-dev libmysqlclient-dev libnagios-object-perl libnagios-plugin-perl libnet-snmp-perl libnet-snmp-perl libnet-tftp-perl libnet-xmpp-perl libpq-dev libredis-perl librrds-perl libssl-dev libswitch-perl libwww-perl m4 netcat parallel php-cli php-gd postfix python-pip rsyslog runit smbclient snmp snmpd snmp-mibs-downloader unzip python python3 python3-pip 
        # there are some redundant packages here
    
# Part 2. Install nagios core 4.4.5 / plugin 2.3.1
RUN cd /tmp \
    #### core ####
    && wget -O nagioscore.tar.gz https://github.com/NagiosEnterprises/nagioscore/archive/nagios-4.4.5.tar.gz \
    && tar xzf nagioscore.tar.gz \
    && cd /tmp/nagioscore-nagios-4.4.5/ \
    
    # prepare for installation
    && ./configure \ 
        --with-httpd-conf=/etc/apache2/sites-enabled \
        --with-checkresult-dir=/usr/local/nagios/checkresult \
        # modify some configuration during installation
        
    && make all \
    && make install-groups-users \
    && usermod -a -G nagios www-data \
    
    # install nagios core
    && make install \
    && make install-daemoninit \
    && make install-commandmode \
    && make install-config \
    && make install-webconf \
    && a2enmod rewrite \
    && a2enmod cgi \
    
    # customize on some configuration
    && mv /usr/local/nagios/var/rw /usr/local/nagios/pipe \
        # some sockets for nagios
        
    && sed -i s/command_file=/#command_file=/  /usr/local/nagios/etc/nagios.cfg \
    && sed -i s/cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/#cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/ /usr/local/nagios/etc/nagios.cfg \
    # && echo "" > /usr/local/nagios/etc/objects/localhost.cfg \
        # disable some configuration
        
    && echo "# CUSTOMIZATION" >> /usr/local/nagios/etc/nagios.cfg \
    && echo "query_socket=/usr/local/nagios/pipe/nagios.qh" >> /usr/local/nagios/etc/nagios.cfg \
    && echo "command_file=/usr/local/nagios/pipe/nagios.cmd" >> /usr/local/nagios/etc/nagios.cfg \
    && echo "cfg_dir=/usr/local/nagios/etc/custom" >> /usr/local/nagios/etc/nagios.cfg \
    && mkdir -p /usr/local/nagios/etc/custom && chown nagios:nagios /usr/local/nagios/etc/custom \
        # customization on configuration
    
    #### plugin ####
    && apt-get install -y autoconf gcc libc6 libmcrypt-dev make libssl-dev wget bc gawk dc build-essential snmp libnet-snmp-perl gettext \
    && cd /tmp \
    && wget --no-check-certificate -O nagios-plugins.tar.gz https://github.com/nagios-plugins/nagios-plugins/archive/release-2.3.1.tar.gz \
    && tar zxf nagios-plugins.tar.gz \
    && cd /tmp/nagios-plugins-release-2.3.1/ \
    && ./tools/setup \
    && ./configure \
    && make \
    && make install
    
# Part 3. Install python environment
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install virtualenv \
    && cd /usr/local/nagios/libexec \
    && virtualenv -p python3 pybox \
    && ./pybox/bin/pip3 install -r /tmp/requirements.txt

# Part 4. Remove cache
RUN apt-get clean \
    && rm -Rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*
    
# Part 5. startup script
ENTRYPOINT service apache2 restart \
    && service nagios restart \
    && htpasswd -cb /usr/local/nagios/etc/htpasswd.users nagiosadmin ${NAGIOS_PSWD:-nagios} \
    && bash