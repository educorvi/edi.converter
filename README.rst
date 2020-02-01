.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

=============
edi.converter
=============

Mit dem Package werden die Daten einer lokalen Plone-Site gelesen und via XMLRPC ausgeliefert. Auf dem fernen System
muss der Branch xmlrpc des Packages nva.migration installiert sein.

Installation
------------

Install edi.converter by adding it to your buildout::

    [buildout]

    ...

    eggs =
        edi.converter


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/edi.converter/issues
- Source Code: https://github.com/collective/edi.converter
- Documentation: https://docs.plone.org/foo/bar


License
-------

The project is licensed under the GPLv2.
