===============================
IoTronic Panels
===============================

Iotronic plugin for the OpenStack Dashboard

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/iotronic_ui
* Bugs: http://bugs.launchpad.net/None

Features
--------

* TODO

Manual Installation
-------------------

Begin by cloning the Horizon and IoTronic Panels repositories::

    git clone https://github.com/openstack/horizon.git
    git clone https://github.com/openstack/iotronic-ui.git

Install IoTronic Panels with all the dependencies::

    cd iotronic-ui
    pip install -r requirements.txt
    python setup.py install

Copy the Iotronic API and enable the plugin in Horizon::

    cp iotronic_ui/api/iotronic.py /usr/share/openstack-dashboard/openstack_dashboard/api/
    cp iotronic_ui/enabled/_60*.py /usr/share/openstack-dashboard/openstack_dashboard/enabled/

To run horizon with the newly enabled IoTronic Panels plugin restart apache::

    systemctl restart apache2.service

Check the Horizon Login page on your browser and you will see the new Dashboard called "IoT".

Extra info
----------
If you want to enable logs for a better debug follow the following steps or just skip them.::

    mkdir /var/log/horizon
    touch /var/log/horizon/horizon.log
    chown -R horizon:horizon horizon

    vim /etc/openstack-dashboard/local_settings.py

        'formatters': {
            'verbose': {
                'format': '%(asctime)s %(process)d %(levelname)s %(name)s %(message)s'
            },
        },

        ....

        'handlers': {
            ....
            'file': {
                   'level': 'DEBUG',
                   'class': 'logging.FileHandler',
                   'filename': '/var/log/horizon/horizon.log',
                   'formatter': 'verbose',
             },
        },

        ....

        'loggers': {
            ....
            'horizon': {
                ....
                'handlers': ['file'],
                ....
            },
            'openstack_dashboard': {
                ....
                'handlers': ['file'],
                ....
            },
            'iotronic_ui': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }

Verify if Apache Openstack Dashboard Configuration file is correctly set with what follows::

    vim /etc/apache2/conf-available/openstack-dashboard.conf
        WSGIApplicationGroup %{GLOBAL}

    service apache2 reload
    systemctl restart apache2.service
