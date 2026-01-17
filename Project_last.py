# PsychoPy Simon Task

import os
from psychopy import visual, core, event, gui # Core modules for psychophysics
import pandas as pd # For data handling/saving
import numpy as np  # For numerical operations
print(os.getcwd())
# "core" contains various functions used for timing and quitting the experiment.
# "gui" allows you to create a dialog box to collect participant information
# "visual" allows you to draw various stimuli
# "event" allows you to collect responses

# --- 1. Stimuli Data Setup (4*n) Trials) ---
import pandas as pd

# Read the CSV file
df_original = pd.read_csv('stimuli.csv')

#Multiply stimuli
n = 3
df = pd.concat([df_original] * n, ignore_index=True) 
df = df.sample(frac=1)   # sample ->random shuffling, 1=100% of the rows
total_trials = len(df)

# Convert each column to a list
color = df['color'].to_list()
position = df['position'].to_list()
condition = df['condition'].to_list()


print(f"DEBUG: Stimuli data loaded. Total trials: {len(color)}")


# --- 2. Setup and Initialization ---
# Get participant info using a simple dialog box
info_dlg = gui.Dlg(title='Participant Info')
info_dlg.addField('Name: ', 'Tester')
info_dlg.addField('Age: ', '76')
participant_data = info_dlg.show()
participant_name = participant_data["Name: "]
participant_age = participant_data["Age: "]
print(f"DEBUG: Participant Name captured: {participant_name}")

# Initialize the main experiment window (800x600 pixels)
win0 = visual.Window(size=(800, 600), units='pix', color=(-1, -1, -1))
print("DEBUG: PsychoPy Window initialized.")


# Define reusable text objects (TextStim)
text_stimulus = visual.TextStim(win0, text='', bold=True, pos=(0.0, 0.0), color=(1.0, 1.0, 1.0), height=60)
feedback_stim = visual.TextStim(win0, text='', bold=False, pos=(0.0, 0.0), color=(1.0, 1.0, 1.0), height=40)


# Butterflies
purple_butterfly = visual.ImageStim(
    win=win0,
    name='purple_butterfly',
    image='purple_butterfly.png',  
    size=(0.4, 0.4),
    units='height',
    interpolate=True
)

yellow_butterfly = visual.ImageStim(
    win=win0,
    name='yellow_butterfly',
    image='yellow_butterfly.png',
    size=(0.4, 0.4),
    units='height',
    interpolate=True
)

white_butterfly = visual.ImageStim(
    win=win0,
    name='white_butterfly',
    image='white_butterfly.png',
    size=(0.4, 0.4),
    units='height',
    interpolate=True
)

butterflies = {
    "purple": purple_butterfly,
    "yellow": yellow_butterfly
}

# Lists to store the results collected during the experiment
key_pressed = []
reaction_time = []
response_status = [] # 1=Correct, 0=Incorrect, 2=Timeout
conditions = []

# --- Practice Trials ---
# Convert each column to a list
color_practice = df_original['color'].to_list()
position_practice = df_original['position'].to_list()
condition_practice = df_original['condition'].to_list()

# Show Start Screen
#should we use the arrows instead?
welcome_text = visual.TextStim(win0, text=f'You will be shown butterflies on the screen, press "left arrow" if there is a purple one, "right arrow" if there is a yellow one. Press space to start the Practice Trials!', bold=True, pos=(0.0, 0.0), color=(1.0, 1.0, 1.0))
welcome_text.draw()
win0.flip()
print("DEBUG: Instruction screen displayed. Waiting for SPACE key.")
event.waitKeys(keyList=['space'])
print("DEBUG: SPACE key pressed. Starting trials.")

print("DEBUG: len(color_practice) =", len(color_practice))
print("DEBUG: len(df_original) =", len(df_original))



correct_key_map = {"purple": "left", "yellow": "right"}

# The Practice Trial Loop:
for i in range(len(color_practice)): 
    trial_num = i + 1
    print(f"\nDEBUG: --- Starting Trial {trial_num} ---")

    # 3.1 Display Stimuli
    current_butterfly = butterflies[color_practice[i]]
    current_condition = condition_practice[i]

    if position_practice[i] == "left":
        current_butterfly.pos = (-0.5, 0)
        white_butterfly.pos = (0.5, 0)
    else:  # position == "right"
        current_butterfly.pos = (0.5, 0)
        white_butterfly.pos = (-0.5, 0)

    correct_key = correct_key_map[color_practice[i]]

    if position_practice[i] == correct_key:
        current_condition = "congruent"
    else:
        current_condition = "incongruent"
    
    current_butterfly.draw()
    white_butterfly.draw()
    win0.flip() # Show the words immediately

    # Wait for Response
    start_t = core.MonotonicClock() # Start the trial timer
   
    # MODIFICATION: Removed timeStamped=True. The output will now be a list of strings (keys).
    key_pressed_list = event.waitKeys(maxWait=2, keyList=['left', 'right'])

    #changed keys to left and right arrows    
    # Get the elapsed time since the clock started. This is the RT.
    time_taken = start_t.getTime() 
    key_pressed_rn = '0' # Default key press for timeout 
    
    if color_practice[i] == "purple":
        current_correct_answer = "left"  
    else:
        current_correct_answer = "right"

    # Process and Store Results
    if key_pressed_list == None: # key_pressed_list will be None if maxWait is reached
    # Case A: Timeout (2)
        feedback_stim.text = "Too slow! (Trial %d)" % trial_num      
    else:
    # Case B: Response made
    # MODIFICATION: We now access the key directly from the list's first element [0]
        key_pressed_rn = key_pressed_list[0] 

    # Check for correctness
    is_correct = (
    (key_pressed_rn == 'left' and current_correct_answer == "left") or
    (key_pressed_rn == 'right' and current_correct_answer == "right")
    )
    if is_correct:
        feedback_stim.text = "Correct! (Trial %d)" % trial_num
    else:
        feedback_stim.text = "Incorrect! (Trial %d)" % trial_num

    # Show Feedback and Pause
    feedback_stim.draw()
    win0.flip()
    core.wait(0.7)

# Finished-Text
welcome_text.text = "Great, you finished the Practice Trials! You can now continue with the experiment."
welcome_text.draw()
win0.flip()
event.waitKeys(keyList=['space'])

# --- 3. The Core Trial Loop (n*10 iterations) ---

# Show Start Screen
welcome_text = visual.TextStim(win0, text=f'You will be shown butterflies on the screen, press "left arrow" if there is a purple one, "right arrow" if there is a yellow one. Press space to start the {total_trials}-trial test!', bold=True, pos=(0.0, 0.0), color=(1.0, 1.0, 1.0))
welcome_text.draw()
win0.flip()
print("DEBUG: Instruction screen displayed. Waiting for SPACE key.")
event.waitKeys(keyList=['space'])
print("DEBUG: SPACE key pressed. Starting trials.")

event.clearEvents()

# The Core Trial Loop:
for i in range(len(color)): 
    trial_num = i + 1
    print(f"\nDEBUG: --- Starting Trial {trial_num} ---")

    # 3.1 Display Stimuli
    current_butterfly = butterflies[color[i]]
    correct_key = correct_key_map[color[i]]

    if position[i] == correct_key:
        current_condition = "congruent"
    else:
        current_condition = "incongruent"
        
    conditions.append(current_condition)

    print("DEBUG condition:", current_condition)

    if position[i] == "left":
        current_butterfly.pos = (-0.5, 0)
        white_butterfly.pos = (0.5, 0)
    else:  # position == "right"
        current_butterfly.pos = (0.5, 0)
        white_butterfly.pos = (-0.5, 0)

    current_butterfly.draw()
    white_butterfly.draw()

    win0.flip() # Show the words immediately
    print(f"DEBUG: Displaying stimuli: {color[i]} / white (Condition: {current_condition})")

    # 3.2 Wait for Response
    start_t = core.MonotonicClock() # Start the trial timer
    print(f"DEBUG: Clock started at {start_t.getTime():.4f} seconds.")
   
    # MODIFICATION: Removed timeStamped=True. The output will now be a list of strings (keys).
    key_pressed_list = event.waitKeys(maxWait=2, keyList=['left', 'right'])
    
    # Get the elapsed time since the clock started. This is the RT.
    time_taken = start_t.getTime() 
    key_pressed_rn = '0' # Default key press for timeout 
    
    if color[i] == "purple":
        current_correct_answer = "left"  
    else:
        current_correct_answer = "right"


    # 3.3 Process and Store Results
    if key_pressed_list == None: # key_pressed_list will be None if maxWait is reached
        # Case A: Timeout (2)
        response_status.append(2)
        reaction_time.append(2000) # Store 2000ms (2 seconds) for a timeout
        feedback_stim.text = "Too slow! (Trial %d)" % trial_num
        print(f"DEBUG: Timeout (Reaction Time: 2000ms). Correct answer was {current_correct_answer}.")
        
    else:
        # Case B: Response made
        # MODIFICATION: We now access the key directly from the list's first element [0]
        key_pressed_rn = key_pressed_list[0]
        print(f"DEBUG: key pressed data: {key_pressed_list}") 
        reaction_time.append(round(time_taken * 1000, 3)) # Store time in ms

        # Check for correctness
        is_correct = (key_pressed_rn == 'left' and current_correct_answer == "left") or \
                     (key_pressed_rn == 'right' and current_correct_answer == "right")

        if is_correct:
            response_status.append(1) # Correct (1)
            print(f"DEBUG: Correct response '{key_pressed_rn}' (RT: {reaction_time[-1]:.0f}ms).")
        else:
            response_status.append(0) # Incorrect (0)
            print(f"DEBUG: INCORRECT response '{key_pressed_rn}' (RT: {reaction_time[-1]:.0f}ms). Correct was {current_correct_answer}.")
        
        key_pressed.append(key_pressed_rn)
    
        # 3.4 Show Feedback and Pause
    win0.flip()
    core.wait(0.7)

# --- 4. Data Saving and Exit ---

# Create DataFrame to organize all collected data
data = pd.DataFrame({
    "color": color,
    "position": position,
    "condition": condition,
    "key_pressed": key_pressed,
    "response_status": response_status,
    "reaction_time": reaction_time,
    "participant_name": [participant_name]*len(color),
    "participant_age": [participant_age]*len(color)
})


# Create the save folder and filename using the user's name
data_folder = 'participants_data'
    
filename = participant_name.replace(' ', '_') + '_SimonTask_results.csv'
csv_filename = os.path.join(data_folder, filename)
data.to_csv(csv_filename, index=False)

print(f"\nDEBUG: --- Data Saving Complete ---")
print(f"DEBUG: Data saved to: {csv_filename}")
print("\n--- Final Results (n*10 Trials) ---\n")
print(data)
print("\n-------------------------------\n")

# Show End Screen
welcome_text.text = f"{total_trials} trials completed.\n\nThank you for participating!\n\nPress space to exit."

welcome_text.draw()
win0.flip()
event.waitKeys(keyList=['space'])

print("DEBUG: SPACE pressed on end screen. Shutting down.")
win0.close()
core.quit()