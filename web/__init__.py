# -*- coding: UTF-8 -*-
# Copyright (C) 2004-2010 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2007 Sylvain Taverne <taverne.sylvain@gmail.com>
# Copyright (C) 2008 Hervé Cauwelier <herve@oursours.net>
# Copyright (C) 2010 David Versmisse <versmisse@lil.univ-littoral.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from itools
from context import Context, get_context, set_context
from context import select_language
from context import WebLogger
from exceptions import HTTPError, ClientError, ServerError
from exceptions import NotModified
from exceptions import BadRequest, Unauthorized, Forbidden, NotFound
from exceptions import InternalServerError, NotImplemented, BadGateway
from exceptions import ServiceUnavailable, MethodNotAllowed, Conflict
from exceptions import FormError
from headers import Cookie, SetCookieDataType
from messages import INFO, ERROR, MSG_MISSING_OR_INVALID
from server import WebServer
from soup import SoupMessage
from static import StaticContext
from views import BaseView, STLView

__all__ = [
    'SoupMessage',
    'WebServer',
    'WebLogger',
    # Context
    'Context',
    'StaticContext',
    'set_context',
    'get_context',
    'select_language',
    # View-Controller
    'BaseView',
    'STLView',
    # Exceptions
    'BadGateway',
    'BadRequest',
    'ClientError',
    'Conflict',
    'Forbidden',
    'HTTPError',
    'InternalServerError',
    'MethodNotAllowed',
    'NotFound',
    'NotImplemented',
    'NotModified',
    'ServerError',
    'ServiceUnavailable',
    'Unauthorized',
    'FormError',
    # Messages
    'INFO',
    'ERROR',
    'MSG_MISSING_OR_INVALID',
    ]
