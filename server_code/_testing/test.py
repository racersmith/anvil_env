
def run():
    """ Run all tests in the tests module 

    example:
        from ._testing import test
        test.run()
    """
    from . import tests
    import anvil_testing

    anvil_testing.auto.run(tests, quiet=False)
    