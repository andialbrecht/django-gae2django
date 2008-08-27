#
# Copyright 2008 Andi Albrecht <albrecht.andi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implements the mail fetch API.

http://code.google.com/appengine/docs/mail/
"""

from django.core.mail import send_mail as _send_mail


def send_mail(sender, to, subject, body, **kw):
    # FIXME: Don't skip keywords, use EMailMessage.
    # --> http://code.djangoproject.com/ticket/5790
    if isinstance(to, basestring):
        to = [to]
    _send_mail(subject, body, sender, to, fail_silently=True)
