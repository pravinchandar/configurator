### CONFIGURATOR

#### Introduction:

Configurator is a simple system config management tool that can be used to
manage the following resources on a Debian based Operating System.
The architecture of the tool is such that it can be easily extended to add
support more resources types. The config file to the tool is specified via
an easy-to-interpret YAML file.

1. File
2. Package
3. Command


#### Installation:

    unzip configurator.zip
    cd configurator
    bash -x bootstrap.sh (to install the dependencies)

#### Running Configurator:

Modify the hostname (line 1) in `examples/setup_php_page.yaml` to the 
match the host name Configurator is run on.

    cd bin
    ./configurator --config ../examples/setup_php_page.yaml
    curl http://127.0.0.1

##### File Resource Type:

The File resource type can be used to create, update and signal the restart
of different services on a successful update.

The YAML syntax for File Resource Type is as following:

    i-foobar:
        file:
            /var/www/index.php:
                mode: '0755'
                content: "<?php echo '<p>Hello World</p>'; ?>"
                restart:
                    - apache2
            /tmp/bar:
                owner: foouser
                group: root
                mode: '0700'
                clone: /etc/host.conf

This would create a file called `/var/www/index.php` with the content specified
by the 'content' key. Upon a successful 'update' to the PHP file, the service
`apache2` will be restarted.

Also the file called `/tmp/bar` will be created with its contents copied from
the file `/etc/hosts.conf`. The metadata of the newly created file will be set
according to the config above, only if it differs.

##### Package Resource Type:

The Package resource type specifies the list of the packages that needs to be
installed or uninstalled.

The YAML syntax for the Packate resource type is as following:

    precise64:
        package:
            install:
                - apache2
                - php5
                - libapache2-mod-php5
                - curl
            uninstall:
                - tree

This would install the packages `apache2`, `php5`, `libapache2-mod-php5`, 
`curl` and uninstall the package `tree`. 

##### Command Resource Type:

The Command resource type specifies the Unix commands that can be run on the
host. It can signal the services that needs to be restarted after a successful
run and(/or) run the command only if the specified 'test command' exits with 0.

The YAML syntax for the Command resource type is as followsing:

    precise64:
        command:
            'rm -rf /tmp/cool_dir':
                onlyif: 'test -d /tmp/cool_dir'
            'rm /var/www/index.html':
                onlyif: 'test -f /var/www/index.html'
                restart:
                    - apache2

This would run the command to delete the directory `/tmp/cool_dir` *only if* it
exists as specified by the 'onlyif' metaparam.

This would also run the command to delete the `/var/www/index.html` file
satisfying the pre-condition and restarts the `apache2` service.
