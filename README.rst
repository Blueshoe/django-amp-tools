================
Django AMP Tools
================

This project aims to make the implementation of `AMP pages <http://ampproject.org/>`_ in Django more easy.
The ``example`` app should give you a hint on how to use the AMP tools.
Currently there is an external dependency called `purifycss <https://github.com/purifycss/purifycss>`_.

**Please note**: This project is not production ready.

Installation
------------
* Clone project
* Override the ``AMP_CHECK`` variable in your settings to determine whether the current request is a AMP request or not.
* Add the ``{% amp_compress %}`` template tag to the <head> section in your base template. It takes care of your css.
* Surround your base template with the ``{% amplify %}`` template tag. It takes care of your images.
* Don't forget to close both template tags.

Features
--------
The ``{% amp_compress %}`` tag takes care of your css. It puts only applicable css rules into your AMP page. If you haven't
heard of django-compressor, please take a look at the project `here <https://github.com/django-compressor/django-compressor>`_.

The ``{% amplify %}`` template tag inserts all the things you need for a valid AMP page into your HTML's
``<head>``. For more about that see the `Required Markup of AMP pages <https://www.ampproject.org/docs/tutorials/create/basic_markup#required-mark-up>`_.
Furthermore the tags converts your ``<img>`` tags to ``<amp-img>`` tags. Mind the height and width of your images! It's
really important to set those for AMP prerendering your page's layout. Consider using something like `easy_thumbnails <https://github.com/SmileyChris/easy-thumbnails>`_
to control the size of your images. This example from the easy_thumbnails documentation shows how you could do that:

``{% thumbnail obj.picture 200x200 upscale as thumb %}``

``<img src="{{ thumb.url }}" width="{{ thumb.width }}" height="{{ thumb.height }}" />``

ToDos
-----
**AMP components** - This is probably the most critical issue for this project. AMP is based on `components <https://www.ampproject.org/docs/reference/components>`_.
In contrary to the ``<amp-img>`` tag most of those do not have an equivalent representation in the HTML markdown.
*We need to find a way to support those other components.*

**clean up parsing process** - Surely there is a better and more pythonic way to do this.

**remove purifycss dependency** - Removal of dependency. Maybe we should add some custom functionality to make the output css more AMP compatible (e.g. in terms of ``@ms-viewport`` and ``!important``).

**Test** - It would be really nice to have some tests around here.