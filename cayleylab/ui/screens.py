def numbered_choice(prompt, choices):
    # Display numbered choices and return the selected index
    # choices is a list of strings, returns int index or None if user quits
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}) {choice}")
    print("  q) Quit")
    
    while True:
        resp = input("\nChoice: ").strip().lower()
        if resp == 'q':
            return None
        idx = int(resp) - 1
        if 0 <= idx < len(choices):
            return idx
        print("Invalid choice. Try again.")


def ask_int(prompt, default=None):
    # Ask for an integer with optional default
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        resp = input(full_prompt).strip()
        if not resp and default is not None:
            return default
        return int(resp)


def ask_list_of_ints(prompt, default=None):
    # Ask for comma-separated list of integers
    if default is not None:
        default_str = ",".join(map(str, default))
        full_prompt = f"{prompt} [{default_str}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        resp = input(full_prompt).strip()
        if not resp and default is not None:
            return default
        parts = [p.strip() for p in resp.split(',')]
        return [int(p) for p in parts if p]


def ask_yes_no(prompt, default=True):
    # Ask yes/no question
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        resp = input(prompt + suffix).strip().lower()
        if not resp:
            return default
        if resp in ('y', 'yes'):
            return True
        if resp in ('n', 'no'):
            return False
        print("Please enter y or n.")


def ask_choice(prompt, choices, default=None):
    # Ask user to pick from a list of string choices
    choice_str = "/".join(choices)
    if default:
        full_prompt = f"{prompt} [{choice_str}, default={default}]: "
    else:
        full_prompt = f"{prompt} [{choice_str}]: "
    
    while True:
        resp = input(full_prompt).strip().lower()
        if not resp and default:
            return default
        if resp in choices:
            return resp
        print(f"Please enter one of: {choice_str}")


def print_header(title, lines=None):
    # Print a header with title and optional description lines
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    if lines:
        for line in lines:
            print(f"  {line}")
        print()
