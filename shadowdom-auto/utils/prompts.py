HANDLE_COOKIE_PROMPT = """
    Look at this screenshot. Find the button or link to 'Accept all' cookies.
    Consider different languages such as English ('Accept all', 'Allow all') and German ('Alle Akzeptieren').
    Return only its exact text label. If none is found, return 'None'.
    """

CLICK_LOGIN_PROMPT = """
    Look at this screenshot. Find the button or link to 'Log In', 'Sign In', or 'Anmelden'.
    Return only its exact text label.
    Consider different languages such as English ('Log In', 'Sign In') and German ('Anmelden').
    """

CLICK_SIGNUP_PROMPT = """
    Look at this screenshot. Find the button or link to 'Sign Up', 'Register', or 'Registrieren'.
    Return only its exact text label.
    Consider different languages such as English ('Sign Up', 'Register') and German ('Registrieren').
    """

FILL_EMAIL_PROMPT = """
    Look at this screenshot. Find the input field for 'Email or username'.
    Return only its exact placeholder or visible label text.
    Do not include any special characters or quotes.
    Consider different languages and variations for the placeholder text.
    """
