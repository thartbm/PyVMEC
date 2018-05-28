# this is the run-time script that will make sure the whole GUI is started along with all other functionality
try:
    import GUI
    GUI.start()
except Exception as e:
    print(e)
    
