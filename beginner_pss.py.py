import random
import string

def generate_password():
    print("\n--- Python Password Generator ---")
    
    # 1. Prompt and validate password length (minimum 8 characters)
    while True:
        try:
            length = int(input("Enter desired password length (minimum 8): "))
            if length < 8:
                print("Error: Password length must be at least 8 characters. Please try again.")
            else:
                break
        except ValueError:
            print("Error: Please enter a valid integer for the length.")

    # 2. Prompt and validate character type choices (at least 2 types required)
    while True:
        print("\nSelect character types to include (at least 2):")
        use_upper = input("Include uppercase letters? (y/n): ").strip().lower() == 'y'
        use_lower = input("Include lowercase letters? (y/n): ").strip().lower() == 'y'
        use_numbers = input("Include numbers? (y/n): ").strip().lower() == 'y'
        use_symbols = input("Include symbols? (y/n): ").strip().lower() == 'y'

        selected_types_count = sum([use_upper, use_lower, use_numbers, use_symbols])
        
        if selected_types_count >= 2:
            break
        print("Error: You must select at least 2 character types. Please try again.")

    # 3. Build the character pool and ensure representation from selected types
    char_pool = ""
    mandatory_chars = []

    if use_upper:
        char_pool += string.ascii_uppercase
        mandatory_chars.append(random.choice(string.ascii_uppercase))
    if use_lower:
        char_pool += string.ascii_lowercase
        mandatory_chars.append(random.choice(string.ascii_lowercase))
    if use_numbers:
        char_pool += string.digits
        mandatory_chars.append(random.choice(string.digits))
    if use_symbols:
        char_pool += string.punctuation
        mandatory_chars.append(random.choice(string.punctuation))

    # Fill the remaining length with random choices from the full pool
    remaining_length = length - len(mandatory_chars)
    password_list = mandatory_chars + [random.choice(char_pool) for _ in range(remaining_length)]

    # Shuffle to ensure random placement of the mandatory characters
    random.shuffle(password_list)
    final_password = "".join(password_list)

    # 4. Display the generated password
    print(f"\nGenerated Password: {final_password}")

def main():
    # 5. Option to generate another password without restarting the program
    while True:
        generate_password()
        
        choice = input("\nWould you like to generate another password? (y/n): ").strip().lower()
        if choice != 'y':
            print("Exiting Password Generator. Stay secure!")
            break

if __name__ == "__main__":
    main()