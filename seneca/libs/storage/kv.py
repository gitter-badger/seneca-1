# Placeholder

# Will create a table with 3 columns for each contract:
# * key (string, unique)
# * value (serialized to string regardless of type)
# * type info
# always upsert

import seneca.engine.storage.easy_db as db
from seneca.engine.storage.mysql_base import get_str_to_py_cast_func
from seneca.libs.types import datetime

ex = None
name_space = None

str_len = db.str_len

def add_name_space(t_name):
    assert name_space is not None, "KV module namespace has not been set!"
    return name_space + '$' + t_name

class KV(object):
    def __init__(self, underlying_obj):
        self.underlying_obj = underlying_obj

        # TODO: Totally not secure for untrusted contracts. Change this completely!!!
        #if type(underlying_obj) == db.Table:
        #    underlying_obj._name = add_name_space(underlying_obj._name)


    def __call__(self, *args, **kwargs):
        if self.underlying_obj.__name__ == 'run':
            assert ex is not None, 'Mysql executer has not been set.'
            res = self.underlying_obj(ex)
            if hasattr(res, 'rows'):
                if len(res.rows) > 0:
                    v, t = res.rows[0]
                    return get_str_to_py_cast_func(t)(v)
                else:
                    return None
            return res
        else:
            return KV(self.underlying_obj(*args, **kwargs))

    def __getattr__(self, name):
        #print('Called getattr with: ', name)
        whitelist = ('set', 'run', 'get')
        if name in ('create_table',):
            # restricted
            raise AttributeError('Restricted')
        if name in ('_name', 'to_sql'):
            # pass through
            return getattr(self.underlying_obj, name)
        elif hasattr(self.underlying_obj, name):
            a = getattr(self.underlying_obj, name)
            if type(a) == db.Column:
                return a
            else:
                if name in whitelist:
                    return KV(a)
                else:
                    # restricted to upsert only!
                    raise AttributeError('You may only use {} for a KV'.format(whitelist))
        else:
            raise AttributeError('No attribute "{}"'.format(name))

def create_kv(name):
    # assert ex is not None, 'Mysql executer has not been set.'
    column_tuples = [
        ('k', str_len(30), True),
        ('v', str_len(256)),
        ('t', str_len(20))
    ]
    t = db.Table(add_name_space(name), db.AutoIncrementColumn('id'),
        [db.Column(*x) for x in column_tuples]
    )
    t.create_table(if_not_exists=True).run(ex)
    return KV(t)


def drop_kv(t_name):
    assert ex is not None, 'Mysql executer has not been set.'
    t = db.Table.from_existing(add_name_space(t_name)).run(ex)
    res = t.drop_table().run(ex)
    t.underlying_obj = None
    return res


def get_kv(name):
    assert ex is not None, 'Mysql executer has not been set.'
    return KV(db.Table.from_existing(add_name_space(name)).run(ex))

exports = {
    'str_len': str_len,
    'create_kv': create_kv,
    'get_kv': get_kv,
    'drop_kv': drop_kv,
}
