from ._anvil_designer import _READMETemplate

CONTENT = """# ENV
ENV is a flexible environment variable handler that is designed to be compatible with dependency apps.

## Basic Usage
You can use ENV as a way to give flexibility to configuration variable without having to chase down where they live in the code base.
```
from ENV import environ

my_variable = environ.get('MY_VARIABLE', defalut=1234)
print(my_variable)
>> 1234
```
This can be done without any setup other than adding ENV as a dependency.  However, by adding this type of default get to your code you can then ask about what variables are being used in the codebase from the sever console by running:
```
from ENV import environ
environ.VARIABLES
```

```
Environment Variables
in_use:
	No variables in use.
available:
	MY_VARIABLE
```

We can see that `my_variable` is available to override and that we currently do not have any variables in use.

## Setup
To setup the ability to override environment variables we need to create a table. Accelerated data tables is expected.  The code could be modified a bit to remove this requirement.

Create a table called `env` with columns:
* `key` of type `str`
* `value` of type `simple object`
* `info` of type `str`

You can check the setup status in the server console by running:
```
environ.DB
```
Where you should see:
```
ENV Table Status: Ready
	'env' table created
	key, value, info columns found
```
or information on what setup still needs to happen.

## Full Usage
After a table is setup in the parent app we get expanded functionality.

### Overriding default values
The default values of can be overridden by adding a record in the `env` table.  For instance, to override the `MY_VARIABLE` from earlier we can add the record:


`key=MY_VARIABLE, value=9876, info=this is just a test variable to demonstrate ENV usage`


To the `env` table.

Afterwards, when we run the same code block:
```
from ENV import environ
my_variable = environ.get('MY_VARIABLE', defalut=1234)
print(my_variable)
>> 9876
```
We get the overridden value from the table rather than the default.

### Forced Variables
We can force values to be used in the `env` table by no providing any default value when using `get`.  If the value is not setup within the `env` table we will get a `LookupError`.

```
from ENV import environ
url = environ.get('APP_URL')
>> LookupError: environment variable: 'APP_URL' not found
```

After adding the record to the table:
```
url = environ.get('APP_URL')
print(url)
example.com
```

## Variable Tracking
Variables are automatically tracked throughout the code whenever their value is set or retrieved.  This can be helpful for understanding what is available and in use without having to dig through dependency apps or find configuration variables.  This can be done from the server console:
```
from ENV import environ
environ.VARIABLES
```
```
environ.VARIABLES
Environment Variables
in_use:
	APP_URL
available:
	MY_VARIABLE
```

You can also query the names directly:
```
environ.VARIABLES.in_use
environ.VARIABLES.available
environ.VARIABLES.all
```

### Tracking
Tracking is done whenever the value is set or retrieved.  So variables can only be tracked if the code has been executed.

my_module
```
from ENV import environ

app_url = environ.get('APP_URL')
if False:
    my_var = environ.get('MY_VARIABLE', 1234)
```
now from the console:
```
from ENV import environ
environ.VARIABLES
```
```
environ.VARIABLES
Environment Variables
in_use:
	APP_URL
available:
		No variables available
```
You will get no mention of `MY_VARIABLE` because the code was not executed.  You could use this as a feature by selectively getting variables or misuse it to make this look like a bug.  The choice is yours.

# Testing
I'm utilizing `anvil_testing` as a dependency for running my tests.  Tests can be run from the server console:
```
from ._testing import test
test.run()
```
"""




class _README(_READMETemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.readme.content = CONTENT
        
