FROM ubuntu:20.04

### Part I. Nagios
ARG DEBIAN_FRONTEND="noninteractive"

# install newer apache2 due to security issue CVE-2021-44224, CVE-2021-44790
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ondrej/apache2 && \
    apt-get update && \
    apt-get install -y apache2=2.4.54-1+ubuntu20.04.1+deb.sury.org+1 && \
    apt-get clean &&  \
    rm -Rf /var/lib/apt/lists/*

# install required packages
RUN echo postfix postfix/main_mailer_type string "'Internet Site'" | debconf-set-selections &&  \
    echo postfix postfix/mynetworks string "127.0.0.0/8" | debconf-set-selections &&  \
    echo postfix postfix/mailname string nagios.example.com | debconf-set-selections &&  \
    apt-get update && \
    apt-get install -y \
      # apache2 \
      # apache2-utils \
      autoconf \
      automake \
      bc \
      bsd-mailx \
      build-essential \
      dnsutils \
      fping \
      gettext \
      git \
      gperf \
      iputils-ping \
      jq \
      libapache2-mod-php \
      libcache-memcached-perl \
      libcgi-pm-perl \
      libdbd-mysql-perl \
      libdbi-dev \
      libdbi-perl \
      libfreeradius-dev \
      libgdchart-gd2-xpm-dev \
      libgd-gd2-perl \
      libjson-perl \
      libldap2-dev \
      libmonitoring-plugin-perl \
      libmysqlclient-dev \
      libnagios-object-perl \
      libnet-snmp-perl \
      libnet-snmp-perl \
      libnet-tftp-perl \
      libnet-xmpp-perl \
      libpq-dev \
      libradsec-dev \
      libredis-perl \
      librrds-perl \
      libssl-dev \
      libswitch-perl \
      libwww-perl \
      m4 \
      netcat \
      parallel \
      php-cli \
      php-gd \
      postfix \
      python3-pip \
      python3-nagiosplugin \
      rsyslog \
      runit \
      smbclient \
      snmp \
      snmpd \
      snmp-mibs-downloader \
      unzip \
      python \
      && \
    apt-get clean &&  \
    rm -Rf /var/lib/apt/lists/*

# install nagios-core
ARG NAGIOS_CORE_VERSION="4.4.5"
RUN cd /tmp && \
    wget -O nagioscore.tar.gz https://github.com/NagiosEnterprises/nagioscore/archive/nagios-${NAGIOS_CORE_VERSION}.tar.gz && \
    tar xzf nagioscore.tar.gz && \
    cd /tmp/nagioscore-nagios-${NAGIOS_CORE_VERSION}/ && \
    ./configure \
        --with-httpd-conf=/etc/apache2/sites-enabled \
        --with-checkresult-dir=/usr/local/nagios/checkresult \
        && \
        # modify some configuration during installation
    make all && \
    make install-groups-users && \
    usermod -a -G nagios www-data && \
    make install && \
    make install-daemoninit && \
    make install-commandmode && \
    make install-config && \
    make install-webconf && \
    a2enmod rewrite && \
    a2enmod cgi

# install nagio-plugin
ARG NAGIOS_PLUGIN_VERSION="2.3.1"
RUN apt-get update && \
    apt-get install -y \
      autoconf \
      gcc \
      libc6 \
      libmcrypt-dev \
      make \
      libssl-dev \
      wget \
      bc \
      gawk \
      dc \
      build-essential \
      snmp \
      libnet-snmp-perl \
      gettext \
      && \
    cd /tmp && \
    wget --no-check-certificate -O nagios-plugins.tar.gz https://github.com/nagios-plugins/nagios-plugins/archive/release-${NAGIOS_PLUGIN_VERSION}.tar.gz && \
    tar zxf nagios-plugins.tar.gz && \
    cd /tmp/nagios-plugins-release-${NAGIOS_PLUGIN_VERSION}/ && \
    ./tools/setup && \
    ./configure && \
    make && \
    make install && \
    apt-get clean && \
    rm -Rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

### Part II. customized part
# nagios configuration
RUN echo "##### CUSTOMIZATION ####" >> /usr/local/nagios/etc/nagios.cfg && \
    # command and query socket
    sed -i s/command_file=/#command_file=/  /usr/local/nagios/etc/nagios.cfg && \
    echo "command_file=/usr/local/nagios/pipe/nagios.cmd" >> /usr/local/nagios/etc/nagios.cfg && \
    echo "query_socket=/usr/local/nagios/pipe/nagios.qh" >> /usr/local/nagios/etc/nagios.cfg && \
    mv /usr/local/nagios/var/rw /usr/local/nagios/pipe \
    # disable localhost.cfg
    && sed -i s/cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/#cfg_file=\\/usr\\/local\\/nagios\\/etc\\/objects\\/localhost.cfg/ /usr/local/nagios/etc/nagios.cfg \
    # create folder holding etc
    #       built-in: built-in config like cmd
    #       custom: cfg for user freely hooked
    && echo "cfg_dir=/usr/local/nagios/etc/built-in" >> /usr/local/nagios/etc/nagios.cfg \
    && echo "cfg_dir=/usr/local/nagios/etc/custom" >> /usr/local/nagios/etc/nagios.cfg \
    && mkdir -p /usr/local/nagios/etc/built-in \
    && mkdir -p /usr/local/nagios/etc/custom \
    && chown nagios:nagios /usr/local/nagios/etc

# apache2 configuration
COPY ./apache2 /etc/apache2/sites-enabled

# setup runtime
RUN apt-get update && \
    apt-get install -y \
      python3 \
      python3-pip \
      expect \
      &&  \
    pip3 install virtualenv && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# minimal configuration
COPY ./share/opt /opt
COPY ./minimal-config/opt  /opt
    ### template file for /opt
COPY ./minimal-config/etc /usr/local/nagios/etc
COPY ./share/nagios_var /usr/local/nagios/var
COPY ./share/nagios_etc /usr/local/nagios/etc/custom
    ### template file for nagios

# utility
COPY ./utility /root/utility

# monitor module
COPY ./nagios_libexec /usr/local/nagios/libexec
COPY ./nagios_sidecar /usr/local/nagios/sidecar
COPY ./requirements.txt /tmp/requirements.txt
RUN chown -R nagios:nagios /usr/local/nagios/libexec/python && \
    chown -R nagios:nagios /usr/local/nagios/libexec/shell && \
    cd /usr/local/nagios/libexec && \
    virtualenv -p python3 pybox && \
    ./pybox/bin/pip3 install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt

### Part III. entrypoint
COPY ./entrypoint.sh /
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
