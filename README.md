# RFIDlib
This is a simple python library to read and write RFID tags from a Prolific TA2303 rfid writer.

First, you need to have the `pyserial` library.

Then, it works extremely simple.
You only need to instantiate a `RfidDevice()` and use the `read()` and `write()` built-in methods.

For example:


    #Instantiate the object selecting the serial port and the baudrate (many models of this writer use 38400 as baudrate, but I have tried some with 9600)
    reader = RfidDevice(port='COM8',baudrate=38400)
    #Use initialise() and disconnect() in order to keep the serial port open or closed.
    reader.initialise()
    reader.bleep()
    reader.write(8)
    read = reader.read()
    print(read)
    reader.disconnect()

The `write()` function only accepts integers with a length less than 10 digits and returns `True` or `False` if the data was written correctly.

The `read()` function returns `False` if anything failed during the reading or an `str()` variable containing the data of the tag.

Use `bleep()` to get a feedback in case you want to know physically if everything is correct.

And remember to use the `disconnect()` function when you have finalised using the port to avoid issues.
