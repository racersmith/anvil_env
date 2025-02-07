from anvil import app

"""
Expose an endpoint to run tests at when we are in a debug environment.
You will need to publish the debug version before this can be accessed.
"""

if "debug" in app.environment.tags and app.id == 'AFKPYPDLJMH2TYVK':
    import anvil.server
    test_endpoint = "/test"
    print("Tests can be run here:")
    print(f"{anvil.server.get_app_origin('debug')}{test_endpoint}")

    function_name = f"route:{test_endpoint}"
    from anvil._server import registrations
    
    @anvil.server.route(test_endpoint)
    def run() -> anvil.server.HttpResponse:
        from . import tests
        import anvil_testing

        results = anvil_testing.auto.run(tests, quiet=False)
        return anvil.server.HttpResponse(body=results)
