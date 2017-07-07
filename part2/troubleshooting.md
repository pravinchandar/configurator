#### Problem Statement:

The simple configuration management tool that was built during the Part 1
of this exercise is expected to run seamlessly on a given host to deploy
a PHP application.

The host, `ip-172-31-255-198`, however was in a state that prevented Configurator
from deploying the application.

I'll detail my findings below about how I went about solving the issues.

#### Issue 1: Insufficent storage space

I noticed the storage space was to be an issue.It prevented me from downloading
any packages that were pre-requisites for running Configurator.

    root@ip-172-31-255-198:/var/log# df -HT
    Filesystem     Type      Size  Used Avail Use% Mounted on
    udev           devtmpfs  252M   13k  252M   1% /dev
    tmpfs          tmpfs      52M  349k   51M   1% /run
    /dev/xvda1     ext4      8.4G  8.3G     0 100% /
    none           tmpfs     4.1k     0  4.1k   0% /sys/fs/cgroup
    none           tmpfs     5.3M     0  5.3M   0% /run/lock
    none           tmpfs     257M     0  257M   0% /run/shm
    none           tmpfs     105M     0  105M   0% /run/user

I checked to see if the `/` filesystem was running on low on inodes.

    root@ip-172-31-255-198:/var/log# df -i /
    Filesystem     Inodes IUsed  IFree IUse% Mounted on
    /dev/xvda1     524288 58415 465873   12% /

Knowing inode count wasn't the issue, I `du`ed the filesystem to understand
the space usage.

    root@ip-172-31-255-198:/var/log# sudo du -hsx /* --exclude 'proc/*' | sort -rh | head -n 40
    506M    /usr
    181M    /var
    61M    /lib
    25M    /boot
    9.6M    /bin
    ...
    0    /initrd.img

That was give a away that something was amiss. I explored various avenues at
this stage to narrow down the cause of the high disk usage by sifting through
the logs and etc looking for symptoms.

I started exploring the "process management" side of things to see if processes
are good at bookkeeping.

    root@ip-172-31-255-198:~# sudo lsof +L1
    sudo: unable to resolve host ip-172-31-255-198
    COMMAND  PID USER   FD   TYPE DEVICE   SIZE/OFF NLINK  NODE NAME
    named   1473 root    3w   REG  202,1 7436832768     0 26445 /tmp/tmp.rIKbF2vWAM (deleted)

    root@ip-172-31-255-198:~# ls -l /proc/1473/fd
    total 0
    lr-x------ 1 root root 64 Jul  7 01:26 0 -> /dev/null
    l-wx------ 1 root root 64 Jul  7 01:26 1 -> /dev/null
    lr-x------ 1 root root 64 Jul  7 01:26 10 -> /sbin/named
    l-wx------ 1 root root 64 Jul  7 01:26 2 -> /dev/null
    l-wx------ 1 root root 64 Jul  7 01:26 3 -> /tmp/tmp.rIKbF2vWAM (deleted)

Sure enough there was a process that did not clean up a stale file handle, the
size of the descriptor seem to suggest that this was the culprit process.

I checked to see how this command was run and that pointed me to the file itself.
Knowing this wasn't any "system process" although the name of the process seem
to suggest that was the case. I killed the process and reclaimed the space.

    root@ip-172-31-255-198:~# df -HT
    Filesystem     Type      Size  Used Avail Use% Mounted on
    udev           devtmpfs  252M   13k  252M   1% /dev
    tmpfs          tmpfs      52M  349k   51M   1% /run
    /dev/xvda1     ext4      8.4G  855M  7.1G  11% /
    none           tmpfs     4.1k     0  4.1k   0% /sys/fs/cgroup
    none           tmpfs     5.3M     0  5.3M   0% /run/lock
    none           tmpfs     257M     0  257M   0% /run/shm
    none           tmpfs     105M     0  105M   0% /run/user

#### Issue 2: Incorrect name server

APT couldn't resolve package server as the name server entry in /etc/resolv.conf
was pointing to the host itself (perfectly valid, although in this case the
host wasn't running a DNS server)

I fixed the NS entry and updated the resolver.


#### Issue 3: Apache cannot bind on port 80

The Configurator, at this stage, was able to install packages and configure
services. But apache was failing to start, as there was a service already bound
to port 80.

    roott@ip-172-31-255-198:~# ss -lnp | grep 80
    tcp    LISTEN     0      1                      *:80     *:*      users:(("nc",1469,3))
    root@ip-172-31-255-198:/home/ubuntu# kill 1469

I stopped netcat.


#### Issue 4: Firewall preventing access to port 80

The following rule in IPTables that was preventing port 80 access.

	root@ip-172-31-255-198:/etc/apache2# iptables -L
	Chain INPUT (policy ACCEPT)
	target     prot opt source               destination
	DROP       tcp  --  anywhere             anywhere             tcp dpt:http

	Chain FORWARD (policy ACCEPT)
	target     prot opt source               destination

	Chain OUTPUT (policy ACCEPT)
	target     prot opt source               destination

I added a rule to make sure port 80 access was allowed.

	root@ip-172-31-255-198:/etc/apache2# iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT


#### Conclusion:

After having resolved the 4 issues as described above, I was able to deploy
the app and verify that it is working.

	192-168-1-5:~ pravin$ curl -iv http://34.230.88.46/
	*   Trying 34.230.88.46...
	* Connected to 34.230.88.46 (34.230.88.46) port 80 (#0)
	> GET / HTTP/1.1
	> Host: 34.230.88.46
	> User-Agent: curl/7.43.0
	> Accept: */*
	>
	< HTTP/1.1 200 OK
	HTTP/1.1 200 OK
	< Date: Fri, 07 Jul 2017 09:24:37 GMT
	Date: Fri, 07 Jul 2017 09:24:37 GMT
	< Server: Apache/2.4.7 (Ubuntu)
	Server: Apache/2.4.7 (Ubuntu)
	< X-Powered-By: PHP/5.5.9-1ubuntu4.21
	X-Powered-By: PHP/5.5.9-1ubuntu4.21
	< Content-Length: 18
	Content-Length: 18
	< Content-Type: text/html
	Content-Type: text/html
