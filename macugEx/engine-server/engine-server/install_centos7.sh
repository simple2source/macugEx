#!/bin/bash
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# engine function
engine() {
    if ! [ -d python2.7 ]; then
        tar -zxf python2.7.tar.bz
    else
        echo "start setup.py .."
    fi
    
    if ! [ "$(uname -s)" == 'Darwin' ]; then
        source ./activate
    fi
    
    python setup.py
}

# check firewall status
ps cax | grep firewalld > /dev/null
if [ $? -eq 0 ];then
    service stop firewalld
fi

# check wget status
which wget > /dev/null
if [ $? -eq 0 ]; then
    echo "wget installed."
else 
    yum install -y wget
fi

# check grep status
which grep > /dev/null
if [ $? -eq 0 ]; then
    echo "grep installed."
else
    yum install -y grep
fi

# replace centos base mirros
if grep -q aliyun /etc/yum.repos.d/CentOS-Base.repo; then
    echo "mirrors replaced."
else
    echo "replacing mirrors..."
    mkdir /etc/yum.repos.d/backup
    mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup
    wget -qO /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
    yum clean all
    yum makecache
    echo "mirrors replaced."
fi

# check mongodb status
which mongod > /dev/null
if [ $? -eq 0 ]; then
    # check mongodb is running.
    ps cax | grep mongod > /dev/null
    if [ $? -eq 0 ]; then
        echo "mongodb is running."
    else
        echo "mongodb is not running."
        echo "starting mongod..."
        systemctl start mongod
        echo "mongodb started"
    fi
else
    # add mongodb mirror
    echo "mongodb is not installed."
    echo "installing mongodb"
    echo -e "[mongodb-org]\nname=MongoDB Repository\nbaseurl=http://mirrors.aliyun.com/mongodb/yum/redhat/\$releasever/mongodb-org/3.2/x86_64/\ngpgcheck=0\nenabled=1" | tee /etc/yum.repos.d/mongodb-org.repo
    # update yum cache
    #yum update
    # install mongodb
    echo "installing mongodb..."
    yum -y install mongodb-org
    echo "installed mongodb"
    echo "starting mongod..."
    systemctl start mongod
    echo "mongodb started"
fi

# check redis-server status
which redis-server > /dev/null
if [ $? -eq 0 ]; then
    # check redis-server is running.
    ps cax | grep redis > /dev/null
    if [ $? -eq 0 ]; then
        echo "redis-server is running."
    else
        echo "redis-server is not running."
        echo "starting redis-server..."
        systemctl start redis.service
        echo "redis-server started"
    fi
else
    # add redis mirror
    if [ -f /etc/yum.repos.d/epel.repo ]; then
        mv /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel.repo.backup
    fi
    if [ -f /etc/yum.repos.d/epel-testing.repo ]; then
        mv /etc/yum.repos.d/epel-testing.repo /etc/yum.repos.d/epel-testing.repo.backup
    fi
    wget -qO /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
    # install redis
    echo "installing redis..."
    #yum update
    yum install -y redis
    echo "redis installed."
    echo "starting redis..."
    systemctl start redis.service
    echo "redis started."
fi

# check mosquitto status
which mosquitto > /dev/null
if [ $? -eq 0 ]; then
    # check mongodb is running.
    ps cax | grep mosquitto > /dev/null
    if [ $? -eq 0 ]; then
        echo "mosquitto is running."
    else
        echo "mosquitto is not running."
        echo "starting mosquitto..."
        /usr/sbin/mosquitto -d -c /etc/mosquitto/mosquitto.conf > /var/log/mosquitto.log 2>&1
        echo "mosquitto started"
    fi
else
    # add mosquitto mirror
    if [ -f /etc/yum.repos.d/epel.repo ]; then
       mv /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel.repo.backup
    fi
    if [ -f /etc/yum.repos.d/epel-testing.repo ]; then
       mv /etc/yum.repos.d/epel-testing.repo /etc/yum.repos.d/epel-testing.repo.backup
    fi
    wget -qO /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
    # install mosquitto
    echo "installing mosquitto..."
    #yum update
    yum install -y mosquitto
    echo "mosquitto installed."
    echo "starting mosquitto..."
    cp /etc/mosquitto/mosquitto.conf.example /etc/mosquitto/mosquitto.conf
    /usr/sbin/mosquitto -d -c /etc/mosquitto/mosquitto.conf > /var/log/mosquitto.log 2>&1
    echo "mosquitto started."
fi

engine