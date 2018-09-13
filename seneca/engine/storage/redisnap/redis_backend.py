"""
"""
import redis

from seneca.engine.storage.redisnap.commands import *
import seneca.engine.storage.redisnap.resp_types as rtype
#from seneca.engine.storage.redisnap.addresses import *

def bytes_to_rscalar(b):
    if b:
        b = b.decode("utf-8")
    return rtype.make_rscalar(b)


class Executer():
    '''
    Maps command objects to actual Redis commands and runs them, leans heavily
    on redis.py

    TODO: We should efficiently track collisions and decide whether we want to
    use a log of transactions to commit, or create ops from the stored data
    '''
    def __init__(self, host, port):
        self._redis_executer = redis.StrictRedis(host=host, port=port)

    # TODO: decide if this is worth implemeneting
    def purge(self):
       self._redis_executer.flushdb()

    def exists(self, cmd):
        return self._redis_executer.exists(cmd.key)

    def type(self, cmd):
        return rtype.from_resp_str(self._redis_executer.type(cmd.key).decode("utf-8"))

    def asserttype(self, cmd):
        return isinstance(self.get(cmd), cmd.r_type)

    def get(self, cmd):
        return bytes_to_rscalar(self._redis_executer.get(cmd.key))


    def set(self, cmd):
        self._redis_executer.set(cmd.key, cmd.value)

    def incrbywo(self, cmd):
        try:
            self._redis_executer.incr(cmd.key, cmd.amount)
        except redis.exceptions.ResponseError as e:
            if str(e) == 'value is not an integer or out of range':
                raise RedisVauleTypeError('Existing value has wrong type.')
            else:
                raise

    def appendwo(self, cmd):
        self._redis_executer.append(cmd.key, cmd.value)


    def hget(self, cmd):
        return bytes_to_rscalar(self._redis_executer.hget(cmd.key, cmd.field))

    def hset(self, cmd):
        self._redis_executer.hset(cmd.key, cmd.field, cmd.value)

    def hexists(self, cmd):
        try:
            return self._redis_executer.hexists(cmd.key, cmd.field)
        except redis.exceptions.ResponseError as e:
            if e.args[0] == 'WRONGTYPE Operation against a key holding the wrong kind of value':
                raise RedisKeyTypeError('Existing value has wrong type.')
            else:
                raise

    def del_(self, cmd):
        self._redis_executer.delete(cmd.key)


    def lindex(self, cmd):
        try:
            return bytes_to_rscalar(self._redis_executer.lindex(cmd.key, cmd.index))
        except redis.exceptions.ResponseError as e:
            if e.args[0] == 'WRONGTYPE Operation against a key holding the wrong kind of value':
                raise RedisKeyTypeError('Existing value has wrong type.')
            else:
                raise


    def lset(self, cmd):
        try:
            self._redis_executer.lset(cmd.key, cmd.index, cmd.value)
        except redis.exceptions.ResponseError as e:
            if e.args[0] == 'no such key':
                raise RedisKeyTypeError('Cannot LSet an nonexistent key.')
            elif e.args[0] == 'index out of range':
                return RedisListOutOfRange('Index out of range.')
            else:
                raise


    def lpushnr(self, cmd):
        self._redis_executer.lpush(cmd.key, *cmd.value)


    def rpushnr(self, cmd):
        self._redis_executer.rpush(cmd.key, *cmd.value)


    def _pop_base(self, method_name, cmd):
        try:
            return bytes_to_rscalar(getattr(self._redis_executer, method_name)(cmd.key))
        except redis.exceptions.ResponseError as e:
            if e.args[0] == 'WRONGTYPE Operation against a key holding the wrong kind of value':
                raise RedisKeyTypeError('Existing value has wrong type.')
            else:
                raise


    def lpop(self, cmd):
        return self._pop_base('lpop', cmd)


    def rpop(self, cmd):
        return self._pop_base('rpop', cmd)


    def __call__(self, cmd):
        # TODO: Make sure this is efficient and generally okay.

        if isinstance(cmd, Del):
            self.del_(cmd)
        else:
            return getattr(self, cmd.__class__.__name__.lower())(cmd)


def run_tests(deps_provider):


    import doctest, sys
    return doctest.testmod(sys.modules[__name__], extraglobs={**locals()})