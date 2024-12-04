# SARAXSOFT
Saraxsoft is a project that aims to provide a simple and easy-to-use interface for configuring SARAX drone arms.

Here is the overall directory structure of the project:
```bash
.vscode/
    settings.json
assets/
    icons/
        back_dark.png
        back_light.png
        connected.png
        disconnected.png
        logo.png
    images/
        eight-nobg.png
        eight.png
        four_x-nobg.png
        four_x.png
        four-nobg.png
        four.png
        six-nobg.png
        six.png
    favicon.ico
demo/
    .vscode/
        extensions.json
    include/
        README.md
    src/
        main.cpp
    test/
        README.md
    .gitignore
    platformio.ini
saraxsoft/
    common/
        __init__.py
        enums.py
        exceptions.py
    manager/
        __init__.py
        serial.py
    ui/
        common/
            __init__.py
            label_separator.py
            popups.py
        steps/
            __init__.py
            configuration.py
            connection.py
            setup.py
        __init__.py
        app.py
        navigation.py
        state.py
    utils/
        __init__.py
        image_utils.py
        path_resolver.py
    __init__.py
    main.py
    settings.py
tests/
    __init__.py
.gitignore
README.md
pyproject.toml
LICENSE
```

The main application is present in the `saraxsoft` directory. The application itself borrows from the [MVC design pattern](https://www.geeksforgeeks.org/mvc-design-pattern/).

The `__init__.py` file in each directory is used to define the directory as a package. The `main.py` file is the entry point of the application and is used to start the application. Although it is no longer necessary to use the `__init__.py` file to define a package, it is still used in this project for compatibility reasons ([more info here](https://stackoverflow.com/questions/448271/what-is-init-py-for])).

The main components of the application are:
- `common`: Contains common components used across the application such as enums and exceptions. Anything that is shared across the application should be placed here.
- `manager`: Contains the serial manager that is used to communicate with the Arduino. This directory defines the controller aspects of the application.
- `ui`: Contains the main UI components. You can find more information about the UI components below.

## Python UI/Frontend
The Python UI is a simple GUI that allows the user to interact with the Arduino (used for demo purposes). The UI is built using the customtkinter library (a framework built on top of tkinter). The choice of customtkinter was made to allow for a more modern look and feel to the UI.

The UI directory itself is found in the `saraxsoft/ui` directory. The UI is divided into two main components:
- `common`: Contains common components used across the UI such as label separators and popups. If you have a component that is used across multiple steps, it should be placed here.
- `steps`: Contains the main steps of the UI. Each step is a separate file that defines the UI for that step. The steps are:
    - `connection`: Allows the user to view the connection status of the Arduino/Companion Computer. This is the 1st step of the UI.
    - `setup`: This step allows the user to configure the number of arms and the type of arms that are connected to the Arduino. Currently, the UI supports 4 (4-x), 6, and 8 arms. This is the 2nd step of the UI.
    - `configuration`: Allows the user to visually configure the arms. This is the 3rd step of the UI.

Additionally, the `navigation.py` file defines the navigation logic of the UI and normally does not need to be modified. You can use the `add_frame` method to add a new step to the UI. This can be done within the `app.py` file.

In order to keep a consistent state across the UI, the `state.py` file is used to store the state of the UI. This file should be used to store any state that needs to be shared across multiple steps. The state supports an observer pattern, so you can register observers to listen for changes in the state.

## Arduino/Companion Computer Communication

The communication between the Arduino and the Companion Computer is done using the serial port. The `serial.py` file in the `saraxsoft/manager` directory defines the serial manager that is used to communicate with the Arduino. The serial manager is responsible for sending and receiving messages to/from the Arduino.

It also keeps track of the connection status of the Arduino. The serial manager is initialized in the `app.py` file and is passed to each step of the UI. This allows the UI to communicate with the Arduino. It uses the `pyserial` library to communicate with the Arduino.

## Backend

The backend of the application is defined in the `demo` directory. The `main.cpp` file defines the main logic of the application. 

The backend is responsible for processing the commands sent by the UI and performing any serial communication with the Arduino. The backend is written in C++ and uses the `Arduino.h` library to communicate with the Arduino. This is a one-step process and does not require any additional steps.