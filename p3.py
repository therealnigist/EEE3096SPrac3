# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
buzzerPWM = None
accuracyPWN = None
currentGuess = None
value = None
score = 0
name = ""
option = ""

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print(" _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, value, option
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
        end_of_game = False
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    print("1 - " + raw_data[0][0] + " took " + raw_data[0][1] + " guesses")
    print("2 - " + raw_data[1][0] + " took " + raw_data[1][1] + " guesses")
    print("3 - " + raw_data[2][0] + " took " + raw_data[2][1] + " guesses")
    pass


# Setup Pins
def setup():
    global LED_value,LED_accuracy,buzzer,LED_accuracy,buzzerPWM,accuracyPWN
    # Setup board mode
    GPIO.setMode(GPIO.BOARD)

    # Setup regular GPIO
    GPIO.setup(LED_value[0], GPIO.OUT)    
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.setup(LED_value[2], GPIO.OUT)

    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(buzzer, GPIO.OUT)  

    GPIO.setup(btn_submit, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    # Setup PWM channels
    buzzerPWM = GPIO.PWM(buzzer, 0.1)
    accuracyPWN = GPIO.PWM(LED_accuracy, 60)

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback = btn_guess_pressed, bouncetime = 200)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback = btn_increase_pressed, bouncetime = 200)
    
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    num_regs = score_count*4
    # Get the scores
    data = eeprom.read_block(1,num_regs)
    scores = []
    # convert the codes back to ascii
    name = ""
    #count = 0
    for i in range(data):
        if (i+1)%4 != 0:
            name += chr(data[i])
        else:
            tup = (name, data[i])
            scores.append(tup)
            name = ""
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    number_of_scores, scores = fetch_scores()
    global name
    global score
    scores.append(name, score)
    scores.sort(reverse=False, key=myFunc)
    #name_bin = []
    data = []
    eeprom.clear()
    for i in range(scores):
        name_list = list(scores[i][0])
        for j in range(3):
            data.append(ord(name_list[j]))
        data.append(scores[i][1])
    eeprom.write_byte(0, number_of_scores+1)
    eeprom.write_block(1, data)


    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass

def myFunc(tup):
    return tup[1]


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess

    global currentGuess
    if currentGuess == 7:
        currentGuess = 0
    else:
        currentGuess += 1
    temp = bin(guess) + ""
    GPIO.output(LED_value[0], int(temp[-1]))
    GPIO.output(LED_value[1], int(temp[-2]))
    GPIO.output(LED_value[2], int(temp[-3]))
    pass


# Guess button
def btn_guess_pressed(channel):
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    global value, currentGuess, end_of_game, option, name, LED_value, buzzer, LED_accuracy, buzzerPWM, accuracyPWN, score

    if (option == "p"):
        timeTaken = time.time()

        while (GPIO.input(channel) == 0):
            pass
        
        timeTaken = time.time() - timeTaken

        if (timeTaken <= 2):
            if guess == value:
                GPIO.output(LED_value[0],0)
                GPIO.output(LED_value[1],0)
                GPIO.output(LED_value[2],0)
                GPIO.output(buzzer,0)
                GPIO.output(LED_accuracy,0)
                buzzerPWM.stop()
                accuracyPWN.stop()
                print("YOU GOT IT RIGHT!!!")
                print("Your Score is " + score)
                while (len(name) < 3):
                    name = input("Enter a three letter username")
                print("Your score has been saved")
                save_scores()
                currentGuess = None
                score = 0
                value = None
                option = ""
                name = ""
                end_of_game = True
            else:
                score += 1
                accuracy_leds()
                trigger_buzzer()
        else:
            currentGuess = None
            score = 0
            value = None
            option = ""
            name = ""
            end_of_game = True

    pass


# LED Brightness
def accuracy_leds():
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%

    global currentGuess, value
    cycle = int(((8-(abs(value-currentGuess))/8)*100))
    if GPIO.input(LED_accuracy):
        accuracyPWN.ChangeDutyCycle(int((abs(value-currentGuess))))
    else:
        accuracyPWN.start(int((abs(value-currentGuess))))
    pass

# Sound Buzzer
def trigger_buzzer(absoluteValue):
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    global buzzer
    if (GPIO.input(buzzer)):
        buzzer.start(50)

    if (absoluteValue == 3):
        buzzer.ChangeFrequency(1)
    elif (absoluteValue == 2):
        buzzer.ChangeFrequency(2)
    elif (absoluteValue ==1):
        buzzer.ChangeFrequency(4)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
