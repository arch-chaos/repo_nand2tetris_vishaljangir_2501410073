// Box.asm for K = 73
// Draws a 32x20 black box starting at Row 73 (RAM address 18720) while any key is pressed.
// Clears the box when no key is pressed.

(LOOP)
    // Check keyboard status
    @KBD
    D=M
    @SET_WHITE
    D;JEQ           // If KBD == 0, set color to 0 (white)

    @color
    M=-1            // Key pressed: set color to -1 (1111111111111111 = black)
    @INIT_DRAW
    0;JMP

(SET_WHITE)
    @color
    M=0             // No key pressed: set color to 0 (white)

(INIT_DRAW)
    // Start address = SCREEN (16384) + 32 * 73 = 18720
    @18720
    D=A
    @addr
    M=D

    // Counter for 20 rows
    @20
    D=A
    @rows
    M=D

(DRAW_ROW)
    @rows
    D=M
    @LOOP
    D;JEQ           // When 20 rows are done, return to main keyboard poll loop

    // Draw Word 0 (leftmost 16 pixels of current row)
    @color
    D=M
    @addr
    A=M
    M=D

    // Draw Word 1 (next 16 pixels of current row -> total 32 pixels wide)
    @color
    D=M
    @addr
    A=M+1
    M=D

    // Move pointer down by 1 row (+32 words)
    @32
    D=A
    @addr
    M=D+M

    // Decrement remaining row count
    @rows
    M=M-1

    @DRAW_ROW
    0;JMP