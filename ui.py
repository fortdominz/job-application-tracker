# ui.py - User Interface Helpers
# This file handles everything visual in the terminal:
# colors, tables, menus, and prompts.
# None of the data logic lives here - just how things look.

import os
from datetime import datetime, date
from models import STATUSES


# ── Terminal Colors ───────────────────────────────────────────────────────────
# These are special codes that tell the terminal to change text color.
# \033[ starts the code, the number sets the color, and \033[0m resets it back.

COLORS = {
    "bold":    "\033[1m",
    "dim":     "\033[2m",    # Greyed out
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "red":     "\033[31m",
    "blue":    "\033[34m",
    "magenta": "\033[35m",
    "cyan":    "\033[36m",
    "reset":   "\033[0m",    # Goes back to normal
}

# Each status gets its own color so it's easy to spot at a glance
STATUS_COLORS = {
    "Saved":              COLORS["dim"],
    "Applied":            COLORS["blue"],
    "Online Assessment":  COLORS["cyan"],
    "Phone Screen":       COLORS["cyan"],
    "Interview":          COLORS["yellow"],
    "Final Round":        COLORS["magenta"],
    "Offer":              COLORS["green"],
    "Rejected":           COLORS["red"],
    "Withdrawn":          COLORS["dim"],
}


def colorize(color_name, text):
    # Wraps any text in a color, then resets back to normal after
    color_code = COLORS.get(color_name, "")
    return color_code + text + COLORS["reset"]


def colorize_status(status):
    # Same as colorize() but looks up the right color for a given status
    color_code = STATUS_COLORS.get(status, "")
    return color_code + status + COLORS["reset"]


# ── Layout Helpers ────────────────────────────────────────────────────────────

def clear_screen():
    # Clears the terminal so things don't feel cluttered
    # "cls" works on Windows, "clear" works on Mac/Linux
    os.system("cls" if os.name == "nt" else "clear")


def print_divider(character="─", length=60):
    print(colorize("dim", character * length))


def print_header(page_title):
    clear_screen()
    print_divider("═")
    print(colorize("bold", "  🎯 Internship Tracker  ·  " + page_title))
    print_divider("═")
    print()


def wait_for_enter():
    # Pause the screen so the user can read what's on it before going back to the menu
    print()
    input(colorize("dim", "  Press Enter to continue..."))


# ── Deadline Badge ────────────────────────────────────────────────────────────

def get_deadline_badge(deadline_string):
    # Returns a short label that shows how urgent the deadline is.
    # Color changes based on how many days are left.

    if not deadline_string:
        return colorize("dim", "No deadline set")

    try:
        deadline_date = datetime.strptime(deadline_string, "%Y-%m-%d").date()
        days_left = (deadline_date - date.today()).days

        if days_left < 0:
            return colorize("dim", "Expired (" + deadline_string + ")")
        elif days_left <= 3:
            return colorize("red",    "⚠ " + str(days_left) + "d left (" + deadline_string + ")")
        elif days_left <= 7:
            return colorize("yellow", "⏳ " + str(days_left) + "d left (" + deadline_string + ")")
        else:
            return colorize("green",  "✓ " + str(days_left) + "d left (" + deadline_string + ")")

    except ValueError:
        # If the date string is somehow malformed, just show it as-is
        return deadline_string


# ── Application Table ─────────────────────────────────────────────────────────

def print_applications_table(applications):
    # Prints all applications in a neat table with columns

    if len(applications) == 0:
        print(colorize("dim", "  No applications found."))
        return

    # How wide each column should be (in characters)
    id_width       = 4
    company_width  = 20
    role_width     = 26
    status_width   = 18

    # Print the column headers
    print(
        colorize("bold", "  " + "ID".ljust(id_width)) +
        colorize("bold", "  " + "Company".ljust(company_width)) +
        colorize("bold", "  " + "Role".ljust(role_width)) +
        colorize("bold", "  " + "Status".ljust(status_width)) +
        colorize("bold", "  " + "Deadline")
    )
    print_divider()

    # Print one row per application
    for app in applications:
        app_id      = str(app["id"]).ljust(id_width)
        company     = app.get("company", "")[:company_width].ljust(company_width)
        role        = app.get("role",    "")[:role_width].ljust(role_width)
        status_text = app.get("status",  "")
        deadline    = get_deadline_badge(app.get("deadline", ""))

        # Color codes are invisible characters, so we pad based on the raw text length
        status_padding = " " * (status_width - len(status_text))

        print(
            "  " + app_id +
            "  " + company +
            "  " + role +
            "  " + colorize_status(status_text) + status_padding +
            "  " + deadline
        )

    print()


# ── Menus and Prompts ─────────────────────────────────────────────────────────

def print_menu(title, options):
    # Prints a simple numbered menu
    # options should be a list of tuples like: [("1", "View applications"), ("q", "Quit")]

    print(colorize("bold", "  " + title))
    print()

    for key, label in options:
        print("  " + colorize("cyan", "[" + key + "]") + "  " + label)

    print()


def ask(question, default=None):
    # Asks the user a question and returns their answer.
    # If they just press Enter and there's a default, it uses that.

    if default:
        question_with_default = "  " + question + " [" + colorize("dim", default) + "]: "
    else:
        question_with_default = "  " + question + ": "

    answer = input(question_with_default).strip()

    if answer == "" and default is not None:
        return default

    return answer


def pick_from_list(title, options, allow_cancel=True):
    # A general-purpose picker - shows any list of options and returns the chosen one.
    # allow_cancel=True  → user can press 0 or q to cancel, returns None
    # allow_cancel=False → used when a field is required (e.g. when creating a new application)

    print(colorize("bold", "  " + title))
    print()

    for index, option in enumerate(options, start=1):
        print("  " + colorize("cyan", str(index) + ".") + "  " + option)

    # Only show the cancel option if cancelling is allowed
    if allow_cancel:
        print("  " + colorize("dim", "0.  Cancel"))
        prompt_text = "  Enter a number (or 0 to cancel): "
    else:
        prompt_text = "  Enter a number: "

    print()

    while True:
        choice = input(prompt_text).strip().lower()

        # Blank Enter — just re-show the prompt silently, no error message needed
        if choice == "":
            continue

        # 0 or q — cancel if allowed
        if allow_cancel and (choice == "0" or choice == "q"):
            return None

        if choice.isdigit():
            choice_number = int(choice)
            if 1 <= choice_number <= len(options):
                return options[choice_number - 1]

        # Only show the error for actual invalid input, not for blank Enter
        if allow_cancel:
            print(colorize("red", "  Please enter a number between 1 and " + str(len(options)) + ", or 0 to cancel."))
        else:
            print(colorize("red", "  Please enter a number between 1 and " + str(len(options)) + "."))


def pick_status(current_status=None, allow_cancel=True):
    # Shows the full list of statuses and lets the user pick one by number.
    # allow_cancel=True  → user can press 0 or q to cancel, returns None
    # allow_cancel=False → used when a field is required (e.g. when creating a new application)

    print()
    print(colorize("bold", "  Pick a status:"))
    print()

    for index, status_name in enumerate(STATUSES, start=1):
        # Show which one is currently selected
        if status_name == current_status:
            marker = colorize("green", "  ← current")
        else:
            marker = ""

        print("  " + colorize("cyan", str(index) + ".") + "  " + colorize_status(status_name) + marker)

    # Only show the cancel option if cancelling is allowed
    if allow_cancel:
        print("  " + colorize("dim", "0.  Cancel (keep current status)"))
        prompt_text = "  Enter a number (or 0 to cancel): "
    else:
        prompt_text = "  Enter a number: "

    print()

    while True:
        choice = input(prompt_text).strip().lower()

        # Blank Enter — re-show the prompt silently, no error message needed
        if choice == "":
            continue

        # 0 or q — cancel if allowed
        if allow_cancel and (choice == "0" or choice == "q"):
            return None

        if choice.isdigit():
            choice_number = int(choice)
            if 1 <= choice_number <= len(STATUSES):
                return STATUSES[choice_number - 1]

        # Only show the error for actual invalid input, not for blank Enter
        if allow_cancel:
            print(colorize("red", "  Please enter a number between 1 and " + str(len(STATUSES)) + ", or 0 to cancel."))
        else:
            print(colorize("red", "  Please enter a number between 1 and " + str(len(STATUSES)) + "."))


# ── Application Detail View ───────────────────────────────────────────────────

def print_application_detail(app):
    # Prints every field of a single application in a clean, readable layout.
    # This is the "expanded" view — the full picture of one application.

    print_divider("─")

    # Title line — company and role front and center
    print(colorize("bold", "  " + app.get("company", "") + "  —  " + app.get("role", "")))
    print_divider("─")
    print()

    # Helper to print one labeled row
    # We pad the label so all the values line up in a clean column
    label_width = 14

    def detail_row(label, value):
        # If there's no value, show a dim dash so the row doesn't just look empty
        if not value or value.strip() == "":
            display_value = colorize("dim", "—")
        else:
            display_value = value
        print("  " + colorize("dim", label.ljust(label_width)) + display_value)

    # Print each field
    detail_row("Status",       colorize_status(app.get("status", "")))
    detail_row("Job Type",     app.get("job_type", ""))
    print()
    detail_row("Location",     app.get("location", ""))
    detail_row("Source",       app.get("source", ""))
    print()
    detail_row("Deadline",     get_deadline_badge(app.get("deadline", "")))
    detail_row("Date Applied", app.get("date_applied", ""))
    detail_row("Salary",       app.get("salary", ""))
    print()
    detail_row("Notes",        app.get("notes", ""))
    print()
    detail_row("ID",           str(app.get("id", "")))
    detail_row("Created",      app.get("date_created", "")[:10])   # just the date, not the time
    detail_row("Last Updated", app.get("last_updated", "")[:10])

    print()
    print_divider("─")


# ── Smart Input Helpers ───────────────────────────────────────────────────────
# These replace the basic ask() call for fields that need validation.
# Instead of crashing the whole form on bad input, they re-ask just that field.

def ask_required(question):
    # Keeps asking until the user types something that isn't blank or just spaces.
    # Used for company name and role — the two fields that cannot be empty.
    while True:
        answer = input("  " + question + ": ").strip()

        if answer != "":
            return answer

        # If they pressed Enter with nothing, nudge them with a specific message
        print(colorize("red", "  This field is required — please enter a value."))


def ask_date(question):
    # Keeps asking until the user either leaves it blank (optional) or types a valid date.
    # A valid date must be in YYYY-MM-DD format, e.g. 2026-06-01.
    from datetime import datetime

    while True:
        answer = input("  " + question + "  (YYYY-MM-DD, or Enter to skip): ").strip()

        # Blank is fine — date fields are optional
        if answer == "":
            return ""

        # Check the format before accepting it
        try:
            datetime.strptime(answer, "%Y-%m-%d")
            return answer
        except ValueError:
            # Tell them exactly what went wrong and show a correct example
            print(colorize("red", "  That date format isn't right. Use YYYY-MM-DD — for example: 2026-06-01"))


def ask_date_update(question, current_value):
    # Used on the update screen for date fields.
    # Pressing Enter keeps the current value (same as all other update fields).
    # Typing a new value validates the format before accepting it.
    from datetime import datetime

    while True:
        answer = input("  " + question + " [" + colorize("dim", current_value or "none") + "]: ").strip()

        # Blank means keep the current value — same as all other update fields
        if answer == "":
            return current_value if current_value else ""

        # Validate the format before accepting the new value
        try:
            datetime.strptime(answer, "%Y-%m-%d")
            return answer
        except ValueError:
            print(colorize("red", "  That date format isn't right. Use YYYY-MM-DD — for example: 2026-06-01"))


def pick_job_type(allow_cancel=True):
    # Shows the standard job type list plus an "Other" option at the end.
    # If the user picks Other, they can type in their own job type.
    # This keeps the list clean while not locking anyone out of edge cases.

    from models import JOB_TYPES

    print(colorize("bold", "  Pick a job type (required):"))
    print()

    # Print the standard options
    for index, job_type in enumerate(JOB_TYPES, start=1):
        print("  " + colorize("cyan", str(index) + ".") + "  " + job_type)

    # Other is always the next number after the list
    other_number = len(JOB_TYPES) + 1
    print("  " + colorize("cyan", str(other_number) + ".") + "  Other (type your own)")

    if allow_cancel:
        print("  " + colorize("dim", "0.  Cancel"))
        prompt_text = "  Enter a number (or 0 to cancel): "
    else:
        prompt_text = "  Enter a number: "

    print()

    while True:
        choice = input(prompt_text).strip().lower()

        # Blank Enter — re-prompt silently
        if choice == "":
            continue

        # Cancel if allowed
        if allow_cancel and (choice == "0" or choice == "q"):
            return None

        if choice.isdigit():
            choice_number = int(choice)

            # Picked one of the standard options
            if 1 <= choice_number <= len(JOB_TYPES):
                return JOB_TYPES[choice_number - 1]

            # Picked "Other" — ask them to type their own
            if choice_number == other_number:
                while True:
                    custom = input("  Enter your job type: ").strip()
                    if custom != "":
                        return custom
                    print(colorize("red", "  Please enter a job type."))

        if allow_cancel:
            print(colorize("red", "  Please enter a number between 1 and " + str(other_number) + ", or 0 to cancel."))
        else:
            print(colorize("red", "  Please enter a number between 1 and " + str(other_number) + "."))
