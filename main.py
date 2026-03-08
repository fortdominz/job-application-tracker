# main.py - The Main Program
# This is where everything comes together.
# It runs the menu loop and connects the UI to the database.
# To start the tracker, run: python main.py

import sys
from datetime import datetime, date

import db
import ui
from models import create_application, JOB_TYPES


# ── Startup Deadline Check ────────────────────────────────────────────────────

def show_deadline_warnings():
    # When the app starts, check if any applications have deadlines coming up soon.
    # If so, show a warning at the top of the screen.

    all_applications = db.get_all_applications()
    urgent_applications = []

    for app in all_applications:
        deadline_string = app.get("deadline", "")

        if deadline_string == "":
            continue  # Skip apps with no deadline

        try:
            deadline_date = datetime.strptime(deadline_string, "%Y-%m-%d").date()
            days_left = (deadline_date - date.today()).days

            # Only warn about deadlines within the next 7 days
            if 0 <= days_left <= 7:
                urgent_applications.append((days_left, app))

        except ValueError:
            continue  # Skip if the date is somehow in the wrong format

    # Show the warnings if there are any
    if len(urgent_applications) > 0:
        urgent_applications.sort()  # Sort by most urgent first

        print(ui.colorize("yellow", "  ⚠  Upcoming Deadlines:"))

        for days_left, app in urgent_applications:
            if days_left == 0:
                time_label = "TODAY"
            else:
                time_label = "in " + str(days_left) + " day(s)"

            print("     " + ui.colorize("yellow", time_label) + "  →  " + app["company"] + " · " + app["role"])

        print()


# ── Main Menu ─────────────────────────────────────────────────────────────────

def show_main_menu():
    ui.print_header("Main Menu")

    # Show a count of how many applications exist
    total = len(db.get_all_applications())
    print(ui.colorize("dim", "  " + str(total) + " application(s) on record\n"))

    # Check for urgent deadlines every time the menu loads
    show_deadline_warnings()

    ui.print_menu("What would you like to do?", [
        ("1", "View all applications"),
        ("2", "Add a new application"),
        ("3", "Update an application"),
        ("4", "Delete an application"),
        ("5", "Filter & search"),
        ("6", "Analytics dashboard"),
        ("q", "Quit"),
    ])

    choice = input("  Your choice: ").strip().lower()
    return choice


# ── Screen: View All ─────────────────────────────────────────────────────────

def screen_view_all():
    ui.print_header("All Applications")

    all_apps = db.get_all_applications()
    ui.print_applications_table(all_apps)

    # After showing the table, let the user open one application in full detail
    # or just press Enter to go back to the menu
    print(ui.colorize("dim", "  Enter an ID to view full details, or press Enter to go back."))
    choice = input("  > ").strip()

    # If they just pressed Enter, go back
    if choice == "":
        return

    # If they typed an ID, try to find and show that application
    if choice.isdigit():
        app = db.get_application_by_id(int(choice))

        if app is None:
            print()
            print(ui.colorize("red", "  No application found with ID " + choice + "."))
            ui.wait_for_enter()
            return

        # Show the full detail view
        ui.print_header("Application Detail")
        ui.print_application_detail(app)

        # After viewing, give them quick actions without going all the way back to the menu
        print(ui.colorize("bold", "  What would you like to do?"))
        print()
        print("  " + ui.colorize("cyan", "[u]") + "  Update this application")
        print("  " + ui.colorize("cyan", "[d]") + "  Delete this application")
        print("  " + ui.colorize("cyan", "[b]") + "  Back to all applications")
        print()

        action = input("  Your choice: ").strip().lower()

        if action == "u":
            screen_update_application(prefill_id=app["id"])
        elif action == "d":
            screen_delete_application(prefill_id=app["id"])
        # anything else (including "b") just returns to the menu

    else:
        print()
        print(ui.colorize("red", "  Please enter a valid ID number."))
        ui.wait_for_enter()


# ── Screen: Add Application ───────────────────────────────────────────────────

def screen_add_application():
    ui.print_header("Add New Application")
    print(ui.colorize("dim", "  Fill in the details below. Just press Enter to skip optional fields.\n"))

    try:
        # Collect information from the user
        company      = ui.ask("Company name (required)")
        role         = ui.ask("Role / Job title (required)")
        location     = ui.ask("Location  (e.g. Remote, New York NY)")
        source       = ui.ask("Where did you find it?  (e.g. LinkedIn, Handshake)")
        deadline     = ui.ask("Application deadline  (YYYY-MM-DD)")
        date_applied = ui.ask("Date you applied  (YYYY-MM-DD)")
        salary       = ui.ask("Salary or stipend  (e.g. $8,000/month)")
        notes        = ui.ask("Any notes?  (contacts, links, thoughts)")

        # Let them pick a job type
        # 0 or q cancels the whole add session and goes back to the menu
        # Pressing Enter with no input keeps asking - handled inside pick_from_list()
        print()
        job_type = ui.pick_from_list("Pick a job type (required):", JOB_TYPES, allow_cancel=True)

        if job_type is None:
            print()
            print(ui.colorize("dim", "  Add cancelled. No application was saved."))
            ui.wait_for_enter()
            return

        # Let them pick a status - same rule, 0 or q exits the whole session
        print()
        status = ui.pick_status(allow_cancel=True)

        if status is None:
            print()
            print(ui.colorize("dim", "  Add cancelled. No application was saved."))
            ui.wait_for_enter()
            return

        # Build the application and validate the inputs
        new_app = create_application(
            company      = company,
            role         = role,
            location     = location,
            source       = source,
            status       = status,
            job_type     = job_type,
            date_applied = date_applied,
            deadline     = deadline,
            salary       = salary,
            notes        = notes,
        )

        # Save it to the database
        saved_app = db.add_application(new_app)

        print()
        print(ui.colorize("green", "  ✓ Application saved! (ID: " + str(saved_app["id"]) + ")"))

    except ValueError as error:
        # Something the user typed wasn't valid - show the error message
        print()
        print(ui.colorize("red", "  ✗ Oops: " + str(error)))

    ui.wait_for_enter()


# ── Screen: Update Application ────────────────────────────────────────────────

def screen_update_application(prefill_id=None):
    ui.print_header("Update Application")

    # If we came from the detail view, we already know the ID — skip the table
    if prefill_id is None:
        all_apps = db.get_all_applications()
        ui.print_applications_table(all_apps)

        try:
            app_id = int(ui.ask("Enter the ID of the application to update"))
        except ValueError:
            print(ui.colorize("red", "  That\'s not a valid ID number."))
            ui.wait_for_enter()
            return
    else:
        # ID was passed in directly from the detail view
        app_id = prefill_id

    # Look up the application
    app = db.get_application_by_id(app_id)

    if app is None:
        print(ui.colorize("red", "  No application found with ID " + str(app_id) + "."))
        ui.wait_for_enter()
        return

    print(ui.colorize("bold", "\n  Editing: " + app["company"] + " — " + app["role"]))
    print(ui.colorize("dim",  "  Press Enter to keep the current value shown in brackets.\n"))

    # Collect the updated text fields
    updated_fields = {
        "company":      ui.ask("Company",        app["company"]),
        "role":         ui.ask("Role",            app["role"]),
        "location":     ui.ask("Location",        app["location"]),
        "source":       ui.ask("Source",          app["source"]),
        "deadline":     ui.ask("Deadline",        app["deadline"]),
        "date_applied": ui.ask("Date applied",    app["date_applied"]),
        "salary":       ui.ask("Salary",          app["salary"]),
        "notes":        ui.ask("Notes",           app["notes"]),
    }

    # Handle job type separately using the picker (not a free-text field)
    # We read the current value first - older saved apps might not have this field yet
    current_job_type = app.get("job_type", "")
    print()
    change_job_type = input("  Do you want to update the job type? (y/n): ").strip().lower()

    if change_job_type == "y":
        chosen_job_type = ui.pick_from_list("Pick a job type:", JOB_TYPES)
        if chosen_job_type is None:
            print(ui.colorize("dim", "  Job type update cancelled. Keeping current value."))
            updated_fields["job_type"] = current_job_type
        else:
            updated_fields["job_type"] = chosen_job_type
    else:
        # Keep whatever was already stored (even if it\'s empty for old records)
        updated_fields["job_type"] = current_job_type

    # Handle status separately using the picker
    print()
    change_status = input("  Do you want to update the status? (y/n): ").strip().lower()

    if change_status == "y":
        chosen_status = ui.pick_status(current_status=app["status"])
        if chosen_status is None:
            print(ui.colorize("dim", "  Status update cancelled. Keeping current status."))
            updated_fields["status"] = app["status"]
        else:
            updated_fields["status"] = chosen_status
    else:
        # Keep the original status
        updated_fields["status"] = app["status"]

    # Now compare every field to see if anything actually changed.
    # We use app.get(field, "") for both sides so old records without job_type
    # don\'t cause a false "something changed" result.
    editable_fields = ["company", "role", "job_type", "location", "source",
                       "deadline", "date_applied", "salary", "notes", "status"]

    something_changed = False
    for field in editable_fields:
        original_value = app.get(field, "")
        new_value      = updated_fields.get(field, "")
        if new_value != original_value:
            something_changed = True
            break  # No need to keep checking once we find one change

    if something_changed:
        db.update_application(app_id, updated_fields)
        print()
        print(ui.colorize("green", "  ✓ Application updated!"))
    else:
        print()
        print(ui.colorize("dim", "  No changes were made."))

    ui.wait_for_enter()


# ── Screen: Delete Application ────────────────────────────────────────────────

def screen_delete_application(prefill_id=None):
    ui.print_header("Delete Application")

    # If we came from the detail view, we already know the ID — skip the table
    if prefill_id is None:
        all_apps = db.get_all_applications()
        ui.print_applications_table(all_apps)

        try:
            app_id = int(ui.ask("Enter the ID of the application to delete"))
        except ValueError:
            print(ui.colorize("red", "  That's not a valid ID number."))
            ui.wait_for_enter()
            return
    else:
        # ID was passed in directly from the detail view
        app_id = prefill_id

    # Make sure the application exists
    app = db.get_application_by_id(app_id)

    if app is None:
        print(ui.colorize("red", "  No application found with ID " + str(app_id) + "."))
        ui.wait_for_enter()
        return

    # Ask for confirmation before deleting
    print()
    print(ui.colorize("yellow", "  You're about to delete: " + app["company"] + " — " + app["role"]))
    confirmation = input("  Type 'yes' to confirm: ").strip().lower()

    if confirmation == "yes":
        db.delete_application(app_id)
        print(ui.colorize("green", "  ✓ Application deleted."))
    else:
        print(ui.colorize("dim", "  Cancelled. Nothing was deleted."))

    ui.wait_for_enter()


# ── Screen: Filter & Search ───────────────────────────────────────────────────

def screen_filter_and_search():
    ui.print_header("Filter & Search")

    ui.print_menu("Filter by:", [
        ("1", "Status"),
        ("2", "Company name"),
        ("3", "Deadlines in the next 7 days"),
        ("b", "Back to main menu"),
    ])

    choice = input("  Your choice: ").strip().lower()

    if choice == "1":
        # Let them pick a status and show matching applications
        selected_status = ui.pick_status()

        # If they cancelled, go back without showing anything
        if selected_status is None:
            return

        results = db.filter_applications(status=selected_status)
        ui.print_header("Results: " + selected_status)
        ui.print_applications_table(results)

    elif choice == "2":
        # Search by company name keyword
        keyword = ui.ask("Enter a company name to search for")
        results = db.filter_applications(company=keyword)

        ui.print_header("Results for: '" + keyword + "'")
        ui.print_applications_table(results)

    elif choice == "3":
        # Find applications with deadlines within the next 7 days
        all_apps = db.get_all_applications()
        results = []

        for app in all_apps:
            deadline_string = app.get("deadline", "")

            if deadline_string == "":
                continue

            try:
                deadline_date = datetime.strptime(deadline_string, "%Y-%m-%d").date()
                days_left = (deadline_date - date.today()).days

                if 0 <= days_left <= 7:
                    results.append(app)

            except ValueError:
                continue

        ui.print_header("Deadlines in the Next 7 Days")
        ui.print_applications_table(results)

    elif choice == "b":
        return  # Go back to the main menu

    ui.wait_for_enter()


# ── Screen: Analytics (Coming in Phase 5) ────────────────────────────────────

def screen_analytics():
    ui.print_header("Analytics Dashboard")
    print(ui.colorize("dim", "  📊 Analytics coming in Phase 5!\n"))
    ui.wait_for_enter()


# ── App Entry Point ───────────────────────────────────────────────────────────

def run():
    # This dictionary maps menu choices to their screen functions.
    # It's a cleaner alternative to a long chain of if/elif statements.
    screens = {
        "1": screen_view_all,
        "2": screen_add_application,
        "3": screen_update_application,
        "4": screen_delete_application,
        "5": screen_filter_and_search,
        "6": screen_analytics,
    }

    # Keep looping until the user quits
    while True:
        choice = show_main_menu()

        if choice == "q":
            ui.clear_screen()
            print(ui.colorize("cyan", "\n  👋 Good luck with your applications!\n"))
            sys.exit(0)

        elif choice in screens:
            # Call whichever screen function matches the choice
            screens[choice]()

        # If the input doesn't match anything, just loop back to the menu


# This check makes sure run() only starts if we run this file directly.
# It won't run if another file imports main.py.
if __name__ == "__main__":
    run()
