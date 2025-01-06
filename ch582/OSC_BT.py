import asyncio
from bleak import BleakScanner, BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from pythonosc import dispatcher, osc_server

par_notification_characteristic = '0000fff1-0000-1000-8000-00805f9b34fb'
send_characteristic_UUID = '0000ffe1-0000-1000-8000-00805f9b34fb'
par_device_name = 'wildcat'
disconnected_event = asyncio.Event()

# Global variables
TailState = 0
SentState = 0
is_connected = False  # Track connection status
tail_task = None  # Task for checking TailState
osc_server_started = False  # Track whether the OSC server is running

def notification_handler(characteristic: BleakGATTCharacteristic, data):
    print("Received data:", data)

def disc_callback(client):
    global is_connected
    print('Disconnected!')
    is_connected = False
    disconnected_event.set()

def handle_osc_message(unused_addr, value):
    global TailState
    if is_connected:  # Only process if connected
        TailState = 1 if value else 0  # Update global variable
        print("OSC received ", value)
    else:
        print("Device is disconnected, ignoring OSC message.")

async def start_osc_server():
    global osc_server_started
    if not osc_server_started:  # Only start OSC server once
        osc_dispatcher = dispatcher.Dispatcher()
        osc_dispatcher.map("/avatar/parameters/Tail_IsGrabbed", handle_osc_message)

        server = osc_server.AsyncIOOSCUDPServer(("127.0.0.1", 5158), osc_dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()
        print("OSC Server is listening...")
        osc_server_started = True  # Mark OSC server as started
        return transport
    else:
        print("OSC server already running.")

async def checkTail():
    global c
    global TailState
    global SentState
    while is_connected:  # Ensure the device is connected
        if TailState != SentState:
            print("TailState changed:", TailState)
            SentState = TailState
            await c.write_gatt_char(send_characteristic_UUID, bytearray([TailState]))           
        await asyncio.sleep(0.03)  # 30fps

async def manage_checkTail_task():
    global tail_task
    # Cancel the previous task if it's running
    if tail_task and not tail_task.done():
        tail_task.cancel()
        try:
            await tail_task
        except asyncio.CancelledError:
            print("Previous tail checking task cancelled.")

    # Start a new task for checking TailState
    tail_task = asyncio.create_task(checkTail())

async def connect_device():
    global c
    global is_connected
    while True:
        if not is_connected:
            print('Scanning for device...')
            device = await BleakScanner.find_device_by_name(par_device_name, cb=dict(use_bdaddr=False))
            if device is None:
                print('Device not found, retrying in 5 seconds...')
                await asyncio.sleep(5)
                continue

            print('Connecting to device...')
            try:
                c = BleakClient(device, disconnected_callback=disc_callback)
                await c.connect()
                is_connected = True
                print('Connected to device')

                # Start the OSC server if not already started
                await start_osc_server()

                # Start or restart the tail check task
                await manage_checkTail_task()
            except Exception as e:
                print(f"Failed to connect: {e}")
                is_connected = False

        await asyncio.sleep(5)  # Re-attempt every 5 seconds if disconnected

async def main():
    await connect_device()

asyncio.run(main())
