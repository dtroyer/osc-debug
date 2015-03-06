=========
osc-debug
=========

OpenStackClient Debuggin Plugin

**oscdebug** is an OpenStackClient (OSC) plugin that adds some hopefully
useful debugging commands.

Commands
========

auth show
---------

.. program auth show
.. code bash

    osc auth show

Display the authentication options that are presented to the authentication
plugin.

auth type list
--------------

.. program auth type list
.. code bash

    osc auth type list

List the authentication types (plugins) that are available and the entry
point used.

auth type show
--------------

.. program auth type show
.. code bash

    osc auth type show <name>

Show detais of an authentication plugin, currently name and a list of the
options it defines.

plugin list
-----------

.. program plugin list
.. code bash

    osc plugin list

List all of the recognized OSC plugins.

plugin show
-----------

.. program plugin show
.. code bash

    osc plugin show <name>

Show the details of an OSC plugin.
