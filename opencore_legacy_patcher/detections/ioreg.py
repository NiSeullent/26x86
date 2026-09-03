"""
ioreg.py: PyObjc Handling for IOKit
"""

from __future__ import annotations

import sys
from typing import NewType, Union

if sys.platform != "darwin":
    pointer = type(None)

    kern_return_t = NewType("kern_return_t", int)
    boolean_t = int

    io_object_t = NewType("io_object_t", object)
    io_name_t = bytes
    io_string_t = bytes
    io_registry_entry_t = io_object_t
    io_iterator_t = NewType("io_iterator_t", object)

    CFTypeRef = Union[int, float, bytes, dict, list]
    IOOptionBits = int
    mach_port_t = int
    CFAllocatorType = type(None)

    NULL = 0
    kIOMasterPortDefault: mach_port_t = 0
    kNilOptions: IOOptionBits = NULL
    kCFAllocatorDefault = None

    kIORegistryIterateRecursively = 1
    kIORegistryIterateParents = 2

    def IORegistryEntryCreateCFProperties(entry, properties, allocator, options):
        return (0, {})

    def IOServiceMatching(name: bytes) -> dict:
        return {}

    def IOServiceGetMatchingServices(masterPort, matching, existing):
        return (0, None)

    def IOIteratorNext(iterator):
        return None

    def IORegistryEntryGetParentEntry(entry, plane, parent):
        return (0, None)

    def IOObjectRelease(object) -> kern_return_t:
        return 0

    def IORegistryEntryGetName(entry, name):
        return (0, b"")

    def IOObjectGetClass(object, className):
        return (0, b"")

    def IOObjectCopyClass(object) -> str:
        return ""

    def IOObjectCopySuperclassForClass(classname: str) -> str:
        return ""

    def IORegistryEntryGetChildIterator(entry, plane, iterator):
        return (0, None)

    def IORegistryCreateIterator(masterPort, plane, options, iterator):
        return (0, None)

    def IORegistryEntryCreateIterator(entry, plane, options, iterator):
        return (0, None)

    def IORegistryIteratorEnterEntry(iterator) -> kern_return_t:
        return 0

    def IORegistryIteratorExitEntry(iterator) -> kern_return_t:
        return 0

    def IORegistryEntryCreateCFProperty(entry, key, allocator, options):
        return None

    def IORegistryEntryGetPath(entry, plane, path):
        return (0, b"")

    def IORegistryEntryCopyPath(entry, plane) -> str:
        return ""

    def IOObjectConformsTo(object, className) -> boolean_t:
        return 0

    def IORegistryEntryGetLocationInPlane(entry, plane, location):
        return (0, b"")

    def IOServiceNameMatching(name: bytes) -> dict:
        return {}

    def IORegistryEntryGetRegistryEntryID(entry, entryID):
        return (0, 0)

    def IORegistryEntryIDMatching(entryID: int) -> dict:
        return {}

    def IORegistryEntryFromPath(mainPort, path):
        return None

    def ioiterator_to_list(iterator):
        return iter([])

    def corefoundation_to_native(collection):
        return collection

    def native_to_corefoundation(native):
        return native

    def io_name_t_to_str(name):
        return name.partition(b"\0")[0].decode()

    def get_class_inheritance(io_object):
        return []

else:
    import objc

    from CoreFoundation import CFRelease, kCFAllocatorDefault  # type: ignore # pylint: disable=no-name-in-module
    from Foundation import NSBundle  # type: ignore # pylint: disable=no-name-in-module
    from PyObjCTools import Conversion

    IOKit_bundle = NSBundle.bundleWithIdentifier_("com.apple.framework.IOKit")

    # pylint: disable=invalid-name
    io_name_t_ref_out = b"[128c]"  # io_name_t is char[128]
    const_io_name_t_ref_in = b"r*"
    CFStringRef = b"^{__CFString=}"
    CFDictionaryRef = b"^{__CFDictionary=}"
    CFAllocatorRef = b"^{__CFAllocator=}"
    # pylint: enable=invalid-name

    # https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html
    functions = [
        ("IORegistryEntryCreateCFProperties", b"IIo^@" + CFAllocatorRef + b"I"),
        ("IOServiceMatching", CFDictionaryRef + b"r*"),
        ("IOServiceGetMatchingServices", b"II" + CFDictionaryRef + b"o^I"),
        ("IOIteratorNext", b"II"),
        ("IORegistryEntryGetParentEntry", b"IIr*o^I"),
        ("IOObjectRelease", b"II"),
        ("IORegistryEntryGetName", b"IIo" + io_name_t_ref_out),
        ("IOObjectGetClass", b"IIo" + io_name_t_ref_out),
        ("IOObjectCopyClass", CFStringRef + b"I"),
        ("IOObjectCopySuperclassForClass", CFStringRef + CFStringRef),
        ("IORegistryEntryGetChildIterator", b"IIr*o^I"),
        ("IORegistryCreateIterator", b"IIr*Io^I"),
        ("IORegistryEntryCreateIterator", b"IIr*Io^I"),
        ("IORegistryIteratorEnterEntry", b"II"),
        ("IORegistryIteratorExitEntry", b"II"),
        ("IORegistryEntryCreateCFProperty", b"@I" + CFStringRef + CFAllocatorRef + b"I"),
        ("IORegistryEntryGetPath", b"IIr*oI"),
        ("IORegistryEntryCopyPath", CFStringRef + b"Ir*"),
        ("IOObjectConformsTo", b"II" + const_io_name_t_ref_in),
        ("IORegistryEntryGetLocationInPlane", b"II" + const_io_name_t_ref_in + b"o" + io_name_t_ref_out),
        ("IOServiceNameMatching", CFDictionaryRef + b"r*"),
        ("IORegistryEntryGetRegistryEntryID", b"IIo^Q"),
        ("IORegistryEntryIDMatching", CFDictionaryRef + b"Q"),
        ("IORegistryEntryFromPath", b"II" + const_io_name_t_ref_in),
    ]

    variables = [("kIOMasterPortDefault", b"I")]

    # pylint: disable=invalid-name
    pointer = type(None)

    kern_return_t = NewType("kern_return_t", int)
    boolean_t = int

    io_object_t = NewType("io_object_t", object)
    io_name_t = bytes
    io_string_t = bytes

    io_registry_entry_t = io_object_t
    io_iterator_t = NewType("io_iterator_t", io_object_t)

    CFTypeRef = Union[int, float, bytes, dict, list]

    IOOptionBits = int
    mach_port_t = int
    CFAllocatorType = type(kCFAllocatorDefault)

    NULL = 0

    kIOMasterPortDefault: mach_port_t
    kNilOptions: IOOptionBits = NULL

    kIORegistryIterateRecursively = 1
    kIORegistryIterateParents = 2

    # pylint: enable=invalid-name

    def IORegistryEntryCreateCFProperties(entry: io_registry_entry_t, properties: pointer, allocator: CFAllocatorType, options: IOOptionBits) -> tuple[kern_return_t, dict]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOServiceMatching(name: bytes) -> dict:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOServiceGetMatchingServices(masterPort: mach_port_t, matching: dict, existing: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOIteratorNext(iterator: io_iterator_t) -> io_object_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetParentEntry(entry: io_registry_entry_t, plane: io_name_t, parent: pointer) -> tuple[kern_return_t, io_registry_entry_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOObjectRelease(object: io_object_t) -> kern_return_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetName(entry: io_registry_entry_t, name: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOObjectGetClass(object: io_object_t, className: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOObjectCopyClass(object: io_object_t) -> str:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOObjectCopySuperclassForClass(classname: str) -> str:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetChildIterator(entry: io_registry_entry_t, plane: io_name_t, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryCreateIterator(masterPort: mach_port_t, plane: io_name_t, options: IOOptionBits, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryCreateIterator(entry: io_registry_entry_t, plane: io_name_t, options: IOOptionBits, iterator: pointer) -> tuple[kern_return_t, io_iterator_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryIteratorEnterEntry(iterator: io_iterator_t) -> kern_return_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryIteratorExitEntry(iterator: io_iterator_t) -> kern_return_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryCreateCFProperty(entry: io_registry_entry_t, key: str, allocator: CFAllocatorType, options: IOOptionBits) -> CFTypeRef:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetPath(entry: io_registry_entry_t, plane: io_name_t, path: pointer) -> tuple[kern_return_t, io_string_t]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryCopyPath(entry: io_registry_entry_t, plane: bytes) -> str:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOObjectConformsTo(object: io_object_t, className: bytes) -> boolean_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetLocationInPlane(entry: io_registry_entry_t, plane: io_name_t, location: pointer) -> tuple[kern_return_t, bytes]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IOServiceNameMatching(name: bytes) -> dict:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryGetRegistryEntryID(entry: io_registry_entry_t, entryID: pointer) -> tuple[kern_return_t, int]:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryIDMatching(entryID: int) -> dict:  # pylint: disable=invalid-name
        raise NotImplementedError

    def IORegistryEntryFromPath(mainPort: mach_port_t, path: io_string_t) -> io_registry_entry_t:  # pylint: disable=invalid-name
        raise NotImplementedError

    objc.loadBundleFunctions(IOKit_bundle, globals(), functions)  # type: ignore # pylint: disable=no-member
    objc.loadBundleVariables(IOKit_bundle, globals(), variables)  # type: ignore # pylint: disable=no-member

    def ioiterator_to_list(iterator: io_iterator_t):
        item = IOIteratorNext(iterator)
        while item:
            yield item
            item = IOIteratorNext(iterator)
        IOObjectRelease(iterator)

    def corefoundation_to_native(collection):
        if collection is None:
            return None
        native = Conversion.pythonCollectionFromPropertyList(collection)
        CFRelease(collection)
        return native

    def native_to_corefoundation(native):
        return Conversion.propertyListFromPythonCollection(native)

    def io_name_t_to_str(name):
        return name.partition(b"\0")[0].decode()

    def get_class_inheritance(io_object):
        classes = []
        cls = IOObjectCopyClass(io_object)
        while cls:
            classes.append(cls)
            CFRelease(cls)
            cls = IOObjectCopySuperclassForClass(cls)
        return classes
