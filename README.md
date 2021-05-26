# PyMegatools - A Simple Python Wrapper for [megatools](https://megatools.megous.com/)

This is a Simple Python Library for the [megatools](https://megatools.megous.com/) command line utility 

As of right now, you can use this library to download a file or get it's name from mega.nz


## Installation

You can either install it from PyPi
```shell
pip install pymegatools
```

or traditionally with [setup.py](setup.py)
```shell
python3 setup.py install
```

## A quick example

This example shows how to use this library to download any file from mega.nz

```python
from pymegatools import Megatools

# Initialization
# By default the linux x86_64 or windows64 binary is loaded depending on your platform
mega = Megatools()

# Or you can get the official megatools static binaries for your platform at https://megatools.megous.com/builds/experimental/
# And load it like this:
mega = Megatools(executable='path/to/megatools')

# Get version of the currrent mega binary
print("Version:", mega.version)

url = "https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc"

# Get a file name from url
print(mega.filename(url))

# Downloading a file from url
mega.download(url)
```

The output should look something like:
```shell
Version: 1.11.0
10MB.bin
10MB.bin: 0.00% - 0 bytes of 9.5MiB
10MB.bin: 0.13% - 12.7KiB (13000 bytes) of 9.5MiB (12.4KiB/s)
10MB.bin: 4.28% - 416.4KiB (426400 bytes) of 9.5MiB (401.3KiB/s)
10MB.bin: 21.35% - 2.0MiB (2126800 bytes) of 9.5MiB (1.6MiB/s)
10MB.bin: 36.62% - 3.5MiB (3647800 bytes) of 9.5MiB (1.4MiB/s)
10MB.bin: 53.97% - 5.1MiB (5376800 bytes) of 9.5MiB (1.6MiB/s)
10MB.bin: 69.16% - 6.6MiB (6890000 bytes) of 9.5MiB (1.4MiB/s)
10MB.bin: 88.32% - 8.4MiB (8798400 bytes) of 9.5MiB (1.8MiB/s)
Downloaded 10MB.bin
```

## Passing in a progress callback to modify and redirect the output of downloads
```python
from pymegatools import Megatools

# We define a callback function that accepts
# - The output stream as `stream`
# - The popen Process as `process`
# - A custom argument `prefix`
def progress_callback(stream, process, prefix):
    # A stream is just a list of lines of the output
    # We read the last line in the output stream
    latest_line = stream[-1]
    # And then we append it to a file instead of printing it to the console
    with open('output.txt', 'a+') as f:
        f.write(prefix + latest_line)

# Initializing megatools
mega = Megatools()
url = "https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc"

# Downloading the file and passing in our progress callback
# We also pass in our prefix (the custom argument)
prefix = 'This is the special prefix: '
mega.download(url, progress=progress_callback, progress_arguments=(prefix,)) 
```

Now the output is written to output.txt
```shell
cat output.txt
```

```shell
This is the special prefix: 10MB.bin: 0.00% - 0 bytes of 9.5MiB
This is the special prefix: 10MB.bin: 0.14% - 14.0KiB (14300 bytes) of 9.5MiB (10.9KiB/s)
This is the special prefix: 10MB.bin: 3.99% - 389.7KiB (399100 bytes) of 9.5MiB (374.1KiB/s)
This is the special prefix: 10MB.bin: 22.58% - 2.2MiB (2258100 bytes) of 9.5MiB (1.7MiB/s)
This is the special prefix: 10MB.bin: 44.21% - 4.2MiB (4421300 bytes) of 9.5MiB (2.1MiB/s)
This is the special prefix: 10MB.bin: 63.60% - 6.1MiB (6359600 bytes) of 9.5MiB (1.8MiB/s)
This is the special prefix: 10MB.bin: 83.10% - 7.9MiB (8309600 bytes) of 9.5MiB (1.9MiB/s)
This is the special prefix: 10MB.bin: 98.72% - 9.4MiB (9872200 bytes) of 9.5MiB (1.5MiB/s)
This is the special prefix: Downloaded 10MB.bin
```

## Using Megatools with async progress callbacks
```python
import asyncio
from pymegatools import Megatools

async def main():
    mega = Megatools()
    url = "https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc"

    # To use megatools with the default async callback, simply set assume_async to True and await the result
    await mega.download(url, assume_async=True)

    # OR
    # Use `Megatools.async_download`
    await mega.async_download(url)

    # To use megatools with a custom async progess callback, simply await the download method
    async def async_progress(stream, process):
        # Do async stuff
        print(end=stream[-1])

    await mega.download(url, progress=async_progress)

    # OR
    # Use `Megatools.async_download`
    await mega.async_download(url, progress=async_progress)

asyncio.run(main())
```

## Error Handling
```python
# Pymegatools raises a MegaError if anything goes wrong,
# for example you try to download a file that already exists.

from pymegatools import Megatools, MegaError 
mega = Megatools()
url = "https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc"

# Download file for the first tine
mega.download(url)

# Attempt to download same file again
# Should throw error, so let's catch it.
try:
    mega.download(url)
except MegaError as exception:
    print(f"Error caught {exception}")
```

The output should look something like:
```shell
10MB.bin: 0.00% - 0 bytes of 9.5MiB
10MB.bin: 0.34% - 33.0KiB (33800 bytes) of 9.5MiB (32.9KiB/s)
10MB.bin: 3.21% - 313.4KiB (320872 bytes) of 9.5MiB (278.7KiB/s)
10MB.bin: 15.03% - 1.4MiB (1502800 bytes) of 9.5MiB (1.1MiB/s)
10MB.bin: 24.80% - 2.4MiB (2480400 bytes) of 9.5MiB (949.2KiB/s)
10MB.bin: 31.93% - 3.0MiB (3192800 bytes) of 9.5MiB (693.9KiB/s)
10MB.bin: 40.20% - 3.8MiB (4019600 bytes) of 9.5MiB (807.0KiB/s)
10MB.bin: 43.73% - 4.2MiB (4373200 bytes) of 9.5MiB (211.9KiB/s)
10MB.bin: 43.73% - 4.2MiB (4373200 bytes) of 9.5MiB (0 bytes/s)
10MB.bin: 61.62% - 5.9MiB (6162000 bytes) of 9.5MiB (1.7MiB/s)
10MB.bin: 76.00% - 7.2MiB (7599800 bytes) of 9.5MiB (1.4MiB/s)
10MB.bin: 91.66% - 8.7MiB (9166300 bytes) of 9.5MiB (1.5MiB/s)
10MB.bin: 98.68% - 9.4MiB (9868300 bytes) of 9.5MiB (496.6KiB/s)
10MB.bin: 98.68% - 9.4MiB (9868300 bytes) of 9.5MiB (0 bytes/s)
10MB.bin: 98.70% - 9.4MiB (9869600 bytes) of 9.5MiB (1.3KiB/s)
Downloaded 10MB.bin
ERROR: Download failed for 'https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc': Local file already exists: ./10MB.bin
Error caught [returnCode 1] Download failed for 'https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc': Local file already exists: ./10MB.bin
```



## Credits

[@megous](https://github.com/megous) for making the amazing megatools cmdline utility
