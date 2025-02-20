from ... import environ
from .conftest import _mock


def demo():
    variables = ['example', 'fallback', 'my_secret']
    environments = [
        _mock.published,
        lambda *args: _mock.debug('abc'),
        lambda *args: _mock.debug('bob'),
        _mock.staging,
    ]
    _mock.enable_environments()
    log = list()
    for env in environments:
        env()
        log.append(f"environment.name: '{environ.src.ENVIRONMENT.name}'")
        for var in variables:
            try:
                log.append(f"  environ.get('{var}') = {environ.get(var)}")
            except Exception as e:
                log.append(f"  environ.get('{var}') -> raises {type(e).__name__}: {e}")
        log.append(' ')
    print('\n'.join(log))
    
    