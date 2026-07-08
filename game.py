import random

MIN_NUMBER = 1
MAX_NUMBER = 200


def main():

    games_played = 0
    games_won = 0
    games_lost = 0

    while True:

        print("\n========== GUESS THE NUMBER ==========")
        print("1. Play")
        print("2. High Score")
        print("3. Statistics")
        print("4. Exit")

        choice = input("Enter your choice nga: ")

        if choice == "4":
            print("Thanks for playing idc!")
            break

        elif choice == "2":
            try:
                with open("highscore.txt", "r") as file:
                    print(f"\nHigh Score: {file.read()} guesses\n")
            except FileNotFoundError:
                print("\nNo high score yet.\n")
            continue

        elif choice == "3":
            print("\n===== STATISTICS =====")
            print(f"Games Played : {games_played}")
            print(f"Games Won    : {games_won}")
            print(f"Games Lost   : {games_lost}")

            if games_played > 0:
                win_rate = (games_won / games_played) * 100
                print(f"Win Rate     : {win_rate:.1f}%")

            continue

        elif choice != "1":
            print("Invalid choice.")
            continue

        while True:

            print("\nChoose Difficulty")
            print("1. Easy (15 attempts)")
            print("2. Medium (10 attempts)")
            print("3. Hard (7 attempts) lol")

            difficulty = input("Choice: ")

            if difficulty == "1":
                attempts = 15
            elif difficulty == "2":
                attempts = 10
            elif difficulty == "3":
                attempts = 7
            else:
                print("Invalid choice. Easy selected.")
                attempts = 15

            games_played += 1

            total_attempts = attempts
            secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)

            previous_guesses = []

            print(f"\nGuess a number between {MIN_NUMBER} and {MAX_NUMBER}")

            won = False

            while attempts > 0:

                guess = input("Enter your guess nga: ")

                if not guess.isdigit():
                    print("Please enter a valid number nga.")
                    continue

                guess = int(guess)

                if guess < MIN_NUMBER or guess > MAX_NUMBER:
                    print(f"Enter a number between {MIN_NUMBER} and {MAX_NUMBER}.")
                    continue

                previous_guesses.append(guess)

                difference = abs(secret_number - guess)

                if difference <= 5:
                    print("Hint: Very Close nga!")
                elif difference <= 15:
                    print("Hint: Close nga!")
                elif difference <= 30:
                    print("Hint: A bit far nga.")
                else:
                    print("Hint: Very far nga.")

                if guess == secret_number:

                    won = True
                    games_won += 1

                    guesses_used = total_attempts - attempts + 1

                    try:
                        with open("highscore.txt", "r") as file:
                            highscore = int(file.read())
                    except FileNotFoundError:
                        highscore = None

                    if highscore is None or guesses_used < highscore:
                        with open("highscore.txt", "w") as file:
                            file.write(str(guesses_used))
                        print("New High Score!")

                    print(f"\nCongratulations nga!")
                    print(f"You guessed the number in {guesses_used} guesses.")
                    break

                attempts -= 1

                if guess < secret_number:
                    print("Too low.")
                else:
                    print("Too high.")

                print("Previous guesses:", previous_guesses)
                print(f"Attempts left: {attempts}")

            if not won:
                games_lost += 1
                print(f"\nGame Over! The number was {secret_number} lol.")

            again = input("\nPlay again? (y/n): ").lower()

            if again != "y":
                break


if __name__ == "__main__":
    main()