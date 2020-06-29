FROM ubuntu:16.04

# Part 0. use apt repository in Taiwan
#   if apt installation fails, use the following
# RUN echo "###### Ubuntu Main Repos" > /etc/apt/sources.list \
#    && echo "deb http://tw.archive.ubuntu.com/ubuntu/ xenial main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb-src http://tw.archive.ubuntu.com/ubuntu/ xenial main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "###### Ubuntu Update Repos" >> /etc/apt/sources.list \
#    && echo "deb http://tw.archive.ubuntu.com/ubuntu/ xenial-security main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb http://tw.archive.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb http://tw.archive.ubuntu.com/ubuntu/ xenial-proposed main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb http://tw.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb-src http://tw.archive.ubuntu.com/ubuntu/ xenial-security main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb-src http://tw.archive.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb-src http://tw.archive.ubuntu.com/ubuntu/ xenial-proposed main restricted universe multiverse " >> /etc/apt/sources.list \
#    && echo "deb-src http://tw.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse " >> /etc/apt/sources.list

# Part 1. install required packages
RUN echo postfix postfix/main_mailer_type string "'Internet Site'" | debconf-set-selections \  
    && echo postfix postfix/mynetworks string "127.0.0.0/8" | debconf-set-selections \
    && echo postfix postfix/mailname string nagios.example.com | debconf-set-selections \
    && export DEBIAN_FRONTEND="noninteractive" \
    && apt-get update \
    && apt-get install -y apache2 apache2-utils autoconf automake bc bsd-mailx build-essential dnsutils fping gettext git gperf iputils-ping jq libapache2-mod-php libcache-memcached-perl libcgi-pm-perl libdbd-mysql-perl libdbi-dev libdbi-perl libfreeradius-client-dev libgd2-xpm-dev libgd-gd2-perl libjson-perl libldap2-dev libmysqlclient-dev libnagios-object-perl libnagios-plugin-perl libnet-snmp-perl libnet-snmp-perl libnet-tftp-perl libnet-xmpp-perl libpq-dev libredis-perl librrds-perl libssl-dev libswitch-perl libwww-perl m4 netcat parallel php-cli php-gd postfix python-pip rsyslog runit smbclient snmp snmpd snmp-mibs-downloader unzip python \
        # there are some redundant packages here
    && apt-get install -y python3 python3-pip expect \
    && pip3 install virtualenv \
        # package for customized monitoring package
    && apt-get clean \
    && rm -Rf /var/lib/apt/lists/* 
    
# Part 2. Install nagios core 4.4.5 / plugin 2.3.1
RUN cd /tmp \
    && apt-get update \
    #### nagios core ####
    && wget -O nagioscore.tar.gz https://github.com/NagiosEnterprises/nagioscore/archive/nagios-4.4.5.tar.gz \
    && tar xzf nagioscore.tar.gz \
    && cd /tmp/nagioscore-nagios-4.4.5/ \
    && ./configure \ 
        --with-httpd-conf=/etc/apache2/sites-enabled \
        --with-checkresult-dir=/usr/local/nagios/checkresult \
            # modify some configuration during installation
    && make all \
    && make install-groups-users \
    && usermod -a -G nagios www-data \
    && mkdir -p /home/nagios/.ssh && chown -R nagios:nagios /home/nagios \
    && make install \
    && make install-daemoninit \
    && make install-commandmode \
    && make install-config \
    && make install-webconf \
    && a2enmod rewrite \
    && a2enmod cgi \
    
    #### nagios plugin ####
    && apt-get install -y autoconf gcc libc6 libmcrypt-dev make libssl-dev wget bc gawk dc build-essential snmp libnet-snmp-perl gettext \
    && cd /tmp \
    && wget --no-check-certificate -O nagios-plugins.tar.gz https://github.com/nagios-plugins/nagios-plugins/archive/release-2.3.1.tar.gz \
    && tar zxf nagios-plugins.tar.gz \
    && cd /tmp/nagios-plugins-release-2.3.1/ \
    && ./tools/setup \
    && ./configure \
    && make \
    && make install \
    
    ### Customization on configuration ####
    && echo "# CUSTOMIZATION" >> /usr/local/nagios/etc/nagios.cfg \
    
    # command and query socket
    && sed -i s/command_file=/#command_file=/  /usr/local/nagios/etc/nagios.cfg \
    && echo "command_file=/usr/local/nagios/pipe/nagios.cmd" >> /usr/local/nagios/etc/nagios.cfg \
    && echo "query_socket=/usr/local/nagios/pipe/nagios.qh" >> /usr/local/nagios/etc/nagios.cfg \
    && mv /usr/local/nagios/var/rw /usr/local/nagios/pipe \
    
    # disable localhost.cfg
    && sed -i s/cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/#cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/ /usr/local/nagios/etc/nagios.cfg \
    
    # create folder for customized configuration
    && echo "cfg_dir=/usr/local/nagios/etc/custom" >> /usr/local/nagios/etc/nagios.cfg \
    && mkdir -p /usr/local/nagios/etc/custom \
    && chown nagios:nagios /usr/local/nagios/etc/custom \
    && apt-get clean \
    && rm -Rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* 
    
# Part 3. Provide minimal configuration into image
COPY ./share/opt /opt
COPY ./nagios-template  /opt
    ### template file for /opt    
COPY ./share/nagios_var /usr/local/nagios/var
COPY ./share/nagios_etc /usr/local/nagios/etc/custom
    ### template file for nagios 
COPY ./utility /root/utility
    ### utility for HostOS

# Part 4. Setup customized monitor package of shell, python    
COPY ./nagios_libexec/shell /usr/local/nagios/libexec/shell
COPY ./nagios_libexec/python /usr/local/nagios/libexec/python
COPY ./requirements.txt /tmp/requirements.txt
RUN chown -R nagios:nagios /usr/local/nagios/libexec/python \
    && chown -R nagios:nagios /usr/local/nagios/libexec/shell \
    && cd /usr/local/nagios/libexec \
    && virtualenv -p python3 pybox \
    && ./pybox/bin/pip3 install -r /tmp/requirements.txt

# Part 5. startup script
ENTRYPOINT ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && chown -R nagios:nagios /opt/ssh \
    && service apache2 restart \
    && service nagios restart \
    && htpasswd -cb /usr/local/nagios/etc/htpasswd.users nagiosadmin ${NAGIOS_PSWD:-nagios} \
    && bash