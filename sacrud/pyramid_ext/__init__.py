#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Includeme of SACRUD
"""
import os

import sqlalchemy
import sqlalchemy.orm as orm
from pyramid.path import AssetResolver
from zope.sqlalchemy import ZopeTransactionExtension

from sacrud.common.pyramid_helpers import (get_obj_from_settings,
                                           pkg_prefix, set_jinja2_globals,
                                           set_jinja2_silent_none)
from sacrud.version import __version__


def get_field_template(field):
    ar = AssetResolver()
    path = ar.resolve('sacrud:templates/sacrud/types/%s.jinja2' % field).abspath()
    if os.path.exists(path):
        return path
    return 'sacrud/types/String.jinja2'


def add_routes(config):
    prefix = pkg_prefix(config)
    config.add_route('sa_home',           prefix)
    config.add_route('sa_save_position',  prefix + 'save_position')
    config.add_route('sa_list',           prefix + '{table}')
    config.add_route('sa_create',         prefix + '{table}/create')
    config.add_route('sa_read',           prefix + '{table}/read/{id}')
    config.add_route('sa_update',         prefix + '{table}/update/{id}')
    config.add_route('sa_delete',         prefix + '{table}/delete/{id}')
    config.add_route('sa_paste',          prefix + '{table}/paste/{id}/' +
                                                   '{target_id}')
    config.add_route('sa_paste_tmp',      prefix + '{table}/paste/{id}')


def includeme(config):
    engine = sqlalchemy.engine_from_config(config.registry.settings)
    DBSession = orm.scoped_session(
        orm.sessionmaker(extension=ZopeTransactionExtension()))
    DBSession.configure(bind=engine)

    config.set_request_property(lambda x: DBSession, 'dbsession', reify=True)
    config.set_request_property(
        lambda x: get_obj_from_settings(x, 'sacrud.dashboard_position_model'),
        'sacrud_dashboard_position_model', reify=True)
    config.include(add_routes)
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("sacrud:templates")
    set_jinja2_silent_none(config)

    config.add_static_view('/sa_static', 'sacrud:static')

    jinja2_globals = {'str': str, 'getattr': getattr, 'isinstance': isinstance,
                      'hasattr': hasattr,
                      'session': DBSession,
                      'sqlalchemy': sqlalchemy,
                      'sacrud_ver': __version__,
                      'get_field_template': get_field_template}
    set_jinja2_globals(config, jinja2_globals)
    config.add_jinja2_extension('jinja2.ext.loopcontrols')
    config.scan()
