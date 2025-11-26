# Wriiten by Kenn
import matplotlib.pyplot as plt

weeks_data = {1: {"categories": [], "amounts": []}}
current_week = 1

def add_or_edit_week(week):
    """Adds or edits categories + amounts for a given week."""
    while True:
        print(f"\n--- Editing Week {week} ---")
        category = input("Enter Expense Category: ")
        try:
            amount = float(input("Enter Expense Amount: "))
        except ValueError:
            print("Invalid amount. Please enter a number.")
            continue
        if category in weeks_data[week]["categories"]:
            idx = weeks_data[week]["categories"].index(category)
            weeks_data[week]["amounts"][idx] = amount
        else:
            weeks_data[week]["categories"].append(category)
            weeks_data[week]["amounts"].append(amount)
        c = input("Add/Edit more? Y/N: ").strip().lower()
        if c != "y":
            break

def go_to_next_week():
    """Moves to the next week and copies categories from previous week."""
    global current_week
    prev_week = current_week
    current_week += 1
    if current_week not in weeks_data:
        prev_categories = weeks_data[prev_week]["categories"]
        weeks_data[current_week] = {
            "categories": prev_categories.copy(),
            "amounts": [0 for _ in prev_categories]
        }

    print(f"Now on week {current_week}")

def go_to_previous_week():
    """Moves to the previous week and allows editing."""
    global current_week
    if current_week > 1:
        current_week -= 1
        print(f"Now on week {current_week}")
        add_or_edit_week(current_week)
    else:
        print("Already at the first week.")

def get_total_expenses():
    """Returns a dict {category: total_amount_across_all_weeks}"""
    totals = {}
    for week in weeks_data.values():
        for cat, amt in zip(week["categories"], week["amounts"]):
            totals[cat] = totals.get(cat, 0) + amt
    return totals

def create_pie_chart(): #chart maker/choice 4
    totals = get_total_expenses()
    if not totals:
        print("No expenses recorded across any week.")
        return
    categories = list(totals.keys())
    amounts = list(totals.values())
    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Total Expense Breakdown Across All Weeks")
    plt.axis("equal")
    plt.show()

#menu
def print_menu():
    print("\nExpenses Percentage Calculator")
    print("1.) Add/Edit Expense Categories for Current Week")
    print("2.) Next Expense Period (week only)")
    print("3.) Previous Expense Period (week only)")
    print("4.) Create Pie Chart (Total Across All Weeks)")

#main function
def main():
    global current_week
    while True:
        print_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            add_or_edit_week(current_week)
        elif choice == "2":
            go_to_next_week()
        elif choice == "3":
            go_to_previous_week()
        elif choice == "4":
            create_pie_chart()
        else:
            print("Invalid choice. Select 1, 2, 3, or 4.")

        cont = input("\nContinue? Y/N: ").strip().lower()
        if cont != "y":
            break

main()
