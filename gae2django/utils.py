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

import new


class CallableString(unicode):
    """Helper class providing a callable unicode string.

    This helper class is used to simulate a hybrid user.email attribute.
    App Engine requires this attribute to be callable, returning a string.
    Django expects just a string here.
    CallableString aims to solve this problem.
    """

    def __call__(self):
        return unicode(self)

    def id(self):
        try:
            return int(self.split('_')[-1])
        except:
            return None


def patch_user(user):
    """Patches a instance of Django's builtin User model."""
    if not isinstance(user.email, CallableString):
        user.email = CallableString(user.email)
    if not hasattr(user, 'nickname'):
        nickname = CallableString()
        # TODO(andi): Commented since it's a performance killer.
        #  All tests pass and at least Rietveld seems to run fine.
        #  I'll leave it in the sources in case it comes up again...
#        try:
#            profile = user.get_profile()
#            if hasattr(profile, 'nickname'):
#                nickname = CallableString(profile.nickname)
#        except:
#            pass
        user.nickname = nickname
    if not hasattr(user, 'user_id'):
        user.user_id = new.instancemethod(lambda u: u.id,
                                          user, user.__class__)
