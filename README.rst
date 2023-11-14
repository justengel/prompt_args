===========
prompt_args
===========

Decorator to prompt input for missing arguments.


Install
=======

.. code-block:: shell

    pip install prompt_args


Usage
=====

.. code-block:: python

    from prompt_args import Prompt

    print("Test automatic prompting")
    @Prompt.decorate
    def my_func(first_name: str, last_name: str = "", status: str = "well"):
        print(f"Hello, {first_name} {last_name}, I am {status}")

    my_func()


    print("\nTest controlled prompting")
    @Prompt.decorate(
        first_name=Prompt("First Name: "),
        last_name=Prompt("Last Name: ", default=""),
        status=Prompt("How are you? ", default="well")
    )
    def my_func(first_name: str, last_name: str, **kwargs):
        print(f"Hello, {first_name} {last_name}, I am {kwargs.get('status')}")

    my_func()
    my_func("Jane", "Doe", status="great")

    # Test error when a prompt is given, but the function argument does not exist
    print("\nTest controlled prompt error")
    try:
        @Prompt.decorate(
            first_name=Prompt("First Name: "),
            last_name=Prompt("Last Name: ", default=""),
            status=Prompt("How are you? ", default="well")
        )
        def my_func(first_name: str, last_name: str):
            print(f"Hello, {first_name} {last_name}")
    except ValueError as e:
        assert "no corresponding function argument" in str(e)


Output

.. code-block:: shell

    Test automatic prompting
    Enter First Name: John
    Enter Last Name ['']:
    Enter Status ['well']:
    Hello, John , I am well

    Test controlled prompting
    First Name: John
    Last Name ['']: Doe
    How are you ['well']? just fine
    Hello, John Doe, I am just fine
    Hello, Jane Doe, I am great

    Test controlled prompt error


Register prompt helpers ("Enter ... [{prompt_help}]: ").

.. code-block:: python

    from prompt_args import Prompt

    # Test built in bool converter with Y/n prompt help info
    print("Testing builtin type converter")
    @Prompt.decorate
    def my_func(x: int, confirm: bool = False):
        print(f"Change x to {x}? {confirm}")

    # Test no
    my_func()

    # Test y
    my_func()


    # Test custom type converter
    print("\nTesting custom type converter")
    def long_confirm(value: str) -> bool:
        return value == "Yes I am sure"

    Prompt.register_type_converter(bool, long_confirm, prompt_help="Yes I am sure/no")

    @Prompt.decorate
    def my_super_serious_func(x: int, confirm: bool = False):
        print(f"Change x to {x}? {confirm}")

    # Test invalid y
    my_super_serious_func()

    # Test full Yes I am sure
    my_super_serious_func()

Output:

.. code-block:: shell

    Testing builtin type converter
    Enter X: 10
    Enter Confirm [Y/n]: n
    Change x to 10? False
    Enter X: 12
    Enter Confirm [Y/n]: y
    Change x to 12? True

    Testing custom type converter
    Enter X: 20
    Enter Confirm [Yes I am sure/no]: y
    Change x to 20? False
    Enter X: 25
    Enter Confirm [Yes I am sure/no]: Yes I am sure
    Change x to 25? True
