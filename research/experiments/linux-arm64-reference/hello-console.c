/* SPDX-License-Identifier: MIT */
#include <windows.h>

int main(void)
{
    static const char message[] = "WinFerry Windows console smoke\r\n";
    DWORD written = 0;
    HANDLE output = GetStdHandle(STD_OUTPUT_HANDLE);

    if (output == INVALID_HANDLE_VALUE ||
        !WriteFile(output, message, (DWORD)(sizeof(message) - 1), &written, NULL) ||
        written != sizeof(message) - 1)
        return 2;

    return 37;
}
