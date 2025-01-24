
def run():
    """ Run all tests in the tests module """
    from . import tests
    import anvil_testing

    anvil_testing.auto.run(tests, quiet=False)
    