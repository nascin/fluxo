# Fluxo

![Texto Alternativo da Imagem](https://firebasestorage.googleapis.com/v0/b/teste-nascin-cripto.appspot.com/o/icon-192.png?alt=media&token=ab503840-b47d-4555-8bf4-16347df27d55)

### Simple data flow with execution in separate threads and easy scheduling configuration.

# Installation

To use the `fluxo` library, you can install it using the pip command. Make sure you have Python and pip installed before proceeding.

```
pip install fluxo
```

# How to Use

### 1 - Create a folder in the project root:

First, create a folder named `python_files` at the root of your project. This folder will contain your Python files.

### 2 - Create a Python file within the python_files folder:

Now, create a Python file named fluxo1.py within the python_files folder. This is where you can write your Python code.

### 3 - Write the code:

Write the following code in the fluxo1.py file to create a basic flow with a task:

#### python_files/fluxo1.py:

```
from fluxo.fluxo_core.fluxo import Fluxo
from fluxo.fluxo_core.task import Task

fluxo = Fluxo(
    name='Fluxo 1',
    interval={'minutes': 1, 'at': ':10'})


@Task('Tarefa 1', fluxo=fluxo)
async def my_func():
    print('my_func being executed')
```

### 4 - Finally, start the program with the command below:

```
python -m fluxo.init_schedule
```

### 5 - In another terminal, run the command below to start the web server::

```
python -m fluxo.init_server
```

### 6 - Open browser:

```
http://127.0.0.1:8080
```