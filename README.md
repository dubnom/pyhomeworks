# RFK101 Package

Package to connect to Lutron Homeworks Series-4 and Series-8 systems.
The controller is connected by an RS232 port to an Ethernet adaptor (NPort).

# Example:

    from time import sleep
    from pyhomeworks import Homeworks
    
    def callback(msg,data):
        print(msg,data)

    hw = Homeworks( 'host.test.com', 4008, callback )

    # Sleep for 10 seconds waiting for a callback
    sleep(10.)

    # Close the interface
    hw.close()
