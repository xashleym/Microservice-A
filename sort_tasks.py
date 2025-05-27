import os
import json # Used only for pretty printing the output
from datetime import datetime # Useful for validating date parts

# Define the path to the data file
DATA_FILE = 'tasks.txt'

def parse_task_line(line, line_num):
    """
    Parses a single line from the tasks.txt file into a task dictionary.
    Handles lines with 4 fields (untimed) or 6 fields (timed).
    Returns a task dictionary or None if the line is invalid.
    """
    parts = line.strip().split('|')
    task = {}

    if len(parts) == 4:
        # Untimed task: name|year|month|day
        try:
            task['name'] = parts[0].strip()
            task['year'] = int(parts[1].strip())
            task['month'] = int(parts[2].strip())
            task['day'] = int(parts[3].strip())
            task['hour'] = None # Explicitly set to None
            task['minute'] = None # Explicitly set to None
            # Basic date validation
            datetime(task['year'], task['month'], task['day'])
            return task
        except ValueError:
            print(f"Warning: Skipping invalid data format on line {line_num}: '{line.strip()}' (Date parts must be integers or invalid date)")
            return None
        except IndexError:
             print(f"Warning: Skipping invalid data format on line {line_num}: '{line.strip()}' (Not enough parts for untimed task)")
             return None

    elif len(parts) == 6:
        # Timed task: name|year|month|day|hour|minute
        try:
            task['name'] = parts[0].strip()
            task['year'] = int(parts[1].strip())
            task['month'] = int(parts[2].strip())
            task['day'] = int(parts[3].strip())
            task['hour'] = int(parts[4].strip())
            task['minute'] = int(parts[5].strip())
            # Basic date/time validation
            datetime(task['year'], task['month'], task['day'], task['hour'], task['minute'])
            return task
        except ValueError:
            print(f"Warning: Skipping invalid data format on line {line_num}: '{line.strip()}' (Date/Time parts must be integers or invalid date/time)")
            return None
        except IndexError:
             print(f"Warning: Skipping invalid data format on line {line_num}: '{line.strip()}' (Not enough parts for timed task)")
             return None

    elif not line.strip():
         # Ignore empty lines
         return None

    else:
        # Invalid number of parts
        print(f"Warning: Skipping invalid line format on line {line_num}: '{line.strip()}' (Expected 4 or 6 parts separated by '|')")
        return None

def write_tasks_to_file(tasks):
    """
    Writes the list of task dictionaries back to the tasks.txt file
    in the pipe-delimited format. Overwrites the existing file.
    """
    try:
        with open(DATA_FILE, 'w') as f:
            for task in tasks:
                if task.get('hour') is not None and task.get('minute') is not None:
                    # Timed task format
                    line = f"{task.get('name', '')}|{task.get('year', '')}|{task.get('month', '')}|{task.get('day', '')}|{task.get('hour', '')}|{task.get('minute', '')}\n"
                else:
                    # Untimed task format
                    line = f"{task.get('name', '')}|{task.get('year', '')}|{task.get('month', '')}|{task.get('day', '')}\n"
                f.write(line)
        print(f"Successfully saved tasks to '{DATA_FILE}'.")
    except IOError as e:
        print(f"Error writing to file '{DATA_FILE}': {e}")

def sort_tasks(tasks):
    """
    Sorts a list of task dictionaries.
    Sorting criteria:
    1. Year (ascending)
    2. Month (ascending)
    3. Day (ascending)
    4. Untimed tasks before timed tasks on the same day
    5. Hour (ascending, for timed tasks)
    6. Minute (ascending, for timed tasks)
    """
    def task_sort_key(task):
        """
        Provides a key for sorting based on the task attributes.
        Returns a tuple: (year, month, day, has_time, hour, minute).
        Using float('inf') for hour/minute of untimed tasks ensures they sort last
        among timed tasks on the same day.
        Using 'hour is not None' as the has_time flag (True for timed, False for untimed)
        ensures untimed (False) sort before timed (True) on the same day.
        """
        # Use .get() with a default value (like 0 or float('inf'))
        # This handles cases where a task dictionary might somehow be missing a key
        year = task.get('year', 0)
        month = task.get('month', 0)
        day = task.get('day', 0)

        # Check if hour is not None (indicating a timed task)
        has_time = task.get('hour') is not None

        # Use hour and minute if they exist and are not None, otherwise use infinity
        hour = task.get('hour', float('inf')) if has_time else float('inf')
        minute = task.get('minute', float('inf')) if has_time else float('inf')

        # The key tuple: (year, month, day, has_time_flag, hour, minute)
        # (False sorts before True, so untimed (False) comes before timed (True))
        return (year, month, day, has_time, hour, minute)

    # Sort the tasks using the custom key
    # Create a copy using list() or tasks[:] if you don't want to modify the original list
    sorted_tasks = sorted(tasks, key=task_sort_key)
    return sorted_tasks

def add_task(tasks):
    """Prompts user for task details and adds a new task."""
    print("\n--- Add New Task ---")
    name = input("Enter task name: ").strip()
    if not name:
        print("Task name cannot be empty. Aborting add.")
        return

    while True:
        try:
            year = int(input("Enter year (e.g., 2024): "))
            month = int(input("Enter month (1-12): "))
            day = int(input("Enter day (1-31): "))
            # Basic check if date is valid
            datetime(year, month, day)
            break # Exit loop if date is valid
        except ValueError:
            print("Invalid number entered for year, month, or day. Please try again.")
        except Exception: # Catches invalid dates like Feb 30th
             print("Invalid date entered. Please try again.")


    is_timed = input("Is this a timed task? (y/n): ").strip().lower()
    hour = None
    minute = None

    if is_timed == 'y':
        while True:
            try:
                hour = int(input("Enter hour (0-23): "))
                minute = int(input("Enter minute (0-59): "))
                # Basic time validation (combined with date)
                datetime(year, month, day, hour, minute)
                break # Exit loop if time is valid
            except ValueError:
                print("Invalid number entered for hour or minute. Please try again.")
            except Exception: # Catches invalid times like hour 25
                 print("Invalid time entered. Please try again.")

    new_task = {
        'name': name,
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute
    }

    tasks.append(new_task)
    print("Task added successfully.")
    write_tasks_to_file(tasks) # Save changes immediately

def delete_task(tasks):
    """Prompts user for task index and deletes the task."""
    print("\n--- Delete Task ---")
    if not tasks:
        print("No tasks to delete.")
        return

    print("Current tasks (with index):")
    # Display tasks with index for user to choose
    for i, task in enumerate(tasks):
        time_str = f"{task['hour']:02}:{task['minute']:02}" if task.get('hour') is not None else "Untimed"
        print(f"{i}: {task['name']} - {task['year']}-{task['month']:02}-{task['day']:02} ({time_str})")

    while True:
        try:
            index_to_delete = int(input(f"Enter the index of the task to delete (0 to {len(tasks) - 1}): "))
            if 0 <= index_to_delete < len(tasks):
                # Valid index, proceed with deletion
                deleted_task = tasks.pop(index_to_delete)
                print(f"Deleted task: {deleted_task['name']}")
                write_tasks_to_file(tasks) # Save changes immediately
                break # Exit loop after successful deletion
            else:
                print("Invalid index. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An unexpected error occurred during deletion: {e}")


def main():
    """
    Reads tasks from a text file, provides options to add/delete/sort,
    and saves changes back to the file.
    """
    print("Loading tasks from", DATA_FILE)
    tasks = []
    line_num = 0
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                for line in f:
                    line_num += 1
                    task = parse_task_line(line, line_num)
                    if task: # Only add if parsing was successful and returned a task dict
                        tasks.append(task)
            print(f"Successfully loaded {len(tasks)} tasks.")
        except FileNotFoundError:
             # This case is already handled by os.path.exists, but included for robustness
             print(f"Error: Data file '{DATA_FILE}' not found.")
        except Exception as e:
            print(f"An unexpected error occurred during file reading: {e}")
    else:
        print(f"'{DATA_FILE}' not found. Starting with an empty task list.")


    while True:
        print("\n--- Options ---")
        print("1: Sort and View Tasks")
        print("2: Add New Task")
        print("3: Delete Task")
        print("4: Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            if not tasks:
                print("\nNo tasks to display.")
            else:
                # Make a copy for sorting so the original list order isn't changed unless saved
                tasks_to_sort = list(tasks)
                sorted_tasks = sort_tasks(tasks_to_sort)
                print("\n--- Sorted Tasks ---")
                # Use json.dumps for pretty printing the list of dictionaries
                print(json.dumps(sorted_tasks, indent=2))

        elif choice == '2':
            add_task(tasks) # add_task function handles saving

        elif choice == '3':
            delete_task(tasks) # delete_task function handles saving

        elif choice == '4':
            print("Exiting.")
            break # Exit the main loop

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()
