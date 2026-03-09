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


# ── Sort State ────────────────────────────────────────────────────────────────
# This remembers the chosen sort order for the whole session.
# It lives here in main.py so it persists across multiple visits to the view screen
# without needing to be stored in the database or a file.
current_sort = "id"


# ── Screen: View All ─────────────────────────────────────────────────────────

def screen_view_all():
    global current_sort  # we read and write the session sort state

    # Get the sort label to show in the header so the user knows what's active
    sort_label = next((label for key, label in ui.SORT_OPTIONS if key == current_sort), "Date added")

    ui.print_header("All Applications")

    # Show the active sort so the user always knows what order they're looking at
    print(ui.colorize("dim", "  Sorted by: ") + ui.colorize("cyan", sort_label.split("(")[0].strip()))
    print()

    # Load, sort, and display
    all_apps = db.get_all_applications()
    sorted_apps = db.sort_applications(all_apps, current_sort)
    ui.print_applications_table(sorted_apps)

    # Bottom prompt — sort, open detail, or go back
    print(ui.colorize("dim", "  [s] Change sort    Enter an ID to view details    Enter to go back"))
    print()
    choice = input("  > ").strip().lower()

    # [s] — change sort order
    if choice == "s":
        new_sort = ui.pick_sort_order(current_sort)
        if new_sort is not None:
            current_sort = new_sort
        screen_view_all()  # reload the screen with the new sort applied
        return

    # Blank Enter — go back to menu
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
    print(ui.colorize("dim", "  Fill in the details below. Press Enter to skip optional fields. Type 0 at any picker to cancel.\n"))

    # Required fields — ask_required() keeps re-asking until something is typed
    company = ui.ask_required("Company name (required)")

    # Job type comes right after company — both describe what the job is
    # 0 or q cancels the whole add session and goes back to the menu
    print()
    job_type = ui.pick_job_type(allow_cancel=True)

    if job_type is None:
        print()
        print(ui.colorize("dim", "  Add cancelled. No application was saved."))
        ui.wait_for_enter()
        return

    print()
    role = ui.ask_required("Role / Job title (required)")

    # Optional text fields — plain ask() is fine, blank is allowed
    location = ui.ask("Location  (e.g. Remote, New York NY)")
    source   = ui.ask("Where did you find it?  (e.g. LinkedIn, Handshake)")
    salary   = ui.ask("Salary or stipend  (e.g. $8,000/month)")
    notes    = ui.ask("Any notes?  (contacts, links, thoughts)")

    # Date fields — ask_date() keeps re-asking until format is right or left blank
    deadline     = ui.ask_date("Application deadline")
    date_applied = ui.ask_date("Date you applied")

    # Status picker — same rule, 0 or q exits the whole session
    print()
    status = ui.pick_status(allow_cancel=True)

    if status is None:
        print()
        print(ui.colorize("dim", "  Add cancelled. No application was saved."))
        ui.wait_for_enter()
        return

    # All inputs validated field by field above — this should not raise
    # but we keep the try/except as a safety net just in case
    try:
        new_app   = create_application(
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
        saved_app = db.add_application(new_app)
        print()
        print(ui.colorize("green", "  ✓ Application saved!  (ID: " + str(saved_app["id"]) + ")"))

    except ValueError as error:
        # Safety net — should not normally reach here after field-level validation
        print()
        print(ui.colorize("red", "  ✗ Could not save: " + str(error)))

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

    # Required fields — if blank entered, keep original and warn
    new_company = ui.ask("Company", app["company"])
    if new_company.strip() == "":
        print(ui.colorize("yellow", "  Company name can't be blank — keeping current value."))
        new_company = app["company"]

    new_role = ui.ask("Role", app["role"])
    if new_role.strip() == "":
        print(ui.colorize("yellow", "  Role can't be blank — keeping current value."))
        new_role = app["role"]

    # Optional text fields — blank clears the field
    new_location = ui.ask("Location",   app.get("location", ""))
    new_source   = ui.ask("Source",     app.get("source", ""))
    new_salary   = ui.ask("Salary",     app.get("salary", ""))
    new_notes    = ui.ask("Notes",      app.get("notes", ""))

    # Date fields — validate format, keep original if just Enter pressed
    new_deadline     = ui.ask_date_update("Deadline",     app.get("deadline", ""))
    new_date_applied = ui.ask_date_update("Date applied", app.get("date_applied", ""))

    updated_fields = {
        "company":      new_company,
        "role":         new_role,
        "location":     new_location,
        "source":       new_source,
        "deadline":     new_deadline,
        "date_applied": new_date_applied,
        "salary":       new_salary,
        "notes":        new_notes,
    }

    # Handle job type separately using the picker (not a free-text field)
    # We read the current value first - older saved apps might not have this field yet
    current_job_type = app.get("job_type", "")
    print()
    change_job_type = input("  Do you want to update the job type? (y/n): ").strip().lower()

    if change_job_type == "y":
        chosen_job_type = ui.pick_job_type(allow_cancel=True)
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

    ui.print_menu("Options:", [
        ("1", "Filter by status"),
        ("2", "Filter by company name"),
        ("3", "Deadlines in the next 7 days"),
        ("4", "Keyword search  (searches all fields)"),
        ("5", "Needs attention  (urgent, stalled, incomplete)"),
        ("b", "Back to main menu"),
    ])

    choice = input("  Your choice: ").strip().lower()

    if choice == "1":
        selected_status = ui.pick_status()
        if selected_status is None:
            return
        results = db.filter_applications(status=selected_status)
        ui.print_header("Results: " + selected_status)
        print(ui.colorize("dim", "  " + str(len(results)) + " application(s) found.\n"))
        ui.print_applications_table(results)

    elif choice == "2":
        keyword = ui.ask("Enter a company name to filter by")
        if keyword.strip() == "":
            print(ui.colorize("red", "  Please enter a company name."))
            ui.wait_for_enter()
            return
        results = db.filter_applications(company=keyword)
        ui.print_header("Company filter: '" + keyword + "'")
        print(ui.colorize("dim", "  " + str(len(results)) + " application(s) found.\n"))
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
        print(ui.colorize("dim", "  " + str(len(results)) + " application(s) found.\n"))
        ui.print_applications_table(results)

    elif choice == "4":
        # Keyword search — searches every field of every application
        print()
        keyword = input("  Search all fields: ").strip()

        if keyword == "":
            print(ui.colorize("red", "  Please enter a search term."))
            ui.wait_for_enter()
            return

        results = db.search_applications(keyword)
        ui.print_header("Search results: '" + keyword + "'")

        if len(results) == 0:
            print(ui.colorize("dim", "  No applications matched '" + keyword + "'."))
        else:
            print(ui.colorize("dim", "  " + str(len(results)) + " application(s) found.\n"))
            ui.print_applications_table(results)

    elif choice == "5":
        # Needs attention — surfaces applications that require action
        all_apps = db.get_all_applications()
        flagged  = db.get_needs_attention(all_apps)

        ui.print_header("Needs Attention")
        ui.print_needs_attention(flagged)

    elif choice == "b":
        return

    ui.wait_for_enter()


# ── Screen: Analytics ────────────────────────────────────────────────────────

def screen_analytics():
    ui.print_header("Analytics Dashboard")

    all_apps = db.get_all_applications()

    # If there are no applications yet, nothing to analyse
    if len(all_apps) == 0:
        print(ui.colorize("dim", "  No applications tracked yet. Add some to see analytics.\n"))
        ui.wait_for_enter()
        return

    # Gather all the data we need
    status_counts    = db.get_status_counts(all_apps)
    response_stats   = db.get_response_rate(all_apps)
    monthly_activity = db.get_monthly_activity(all_apps)
    insight          = db.get_quick_insight(all_apps, status_counts, response_stats, monthly_activity)

    # Display each section
    ui.print_status_breakdown(status_counts)
    ui.print_response_rate(response_stats)
    ui.print_monthly_activity(monthly_activity)
    ui.print_quick_insight(insight)

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
