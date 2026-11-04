; KEYS.COM - TSR: reads C:\KEYS.DAT (records: u16 ticks-to-wait, u8 ascii, u8 scan) and stuffs
; each key into the BIOS keyboard buffer from the INT 1Ch timer hook.
org 100h
    jmp init
old:  dd 0
ptr:  dw data
lim:  dw data
wt:   dw 0
isr:
    pushf
    call far [cs:old]
    push ds
    push es
    push ax
    push bx
    push si
    push cs
    pop ds
    mov si,[ptr]
    cmp si,[lim]
    jae .done
    cmp word [wt],0
    je .fire
    dec word [wt]
    jmp .done
.fire:
    mov ax,40h
    mov es,ax
    mov bx,[es:1Ch]
    mov ax,bx
    add ax,2
    cmp ax,[es:82h]
    jb .nw
    mov ax,[es:80h]
.nw:
    cmp ax,[es:1Ah]
    je .done            ; buffer full: retry next tick
    push ax
    mov ax,[si+2]
    mov [es:bx],ax
    pop ax
    mov [es:1Ch],ax
    add si,4
    mov [ptr],si
    cmp si,[lim]
    jae .done
    mov ax,[si]
    mov [wt],ax
.done:
    pop si
    pop bx
    pop ax
    pop es
    pop ds
    iret
init:
    mov ax,3D00h
    mov dx,fname
    int 21h
    jc .err
    mov bx,ax
    mov ah,3Fh
    mov cx,0C000h
    mov dx,data
    int 21h
    jc .err
    add ax,data
    mov [lim],ax
    mov ah,3Eh
    int 21h
    mov si,data
    mov ax,[si]
    mov [wt],ax
    mov ax,351Ch
    int 21h
    mov [old],bx
    mov [old+2],es
    mov ax,251Ch
    mov dx,isr
    int 21h
    mov dx,[lim]
    add dx,15
    mov cl,4
    shr dx,cl
    mov ax,3100h
    int 21h
.err:
    mov ax,4C01h
    int 21h
fname: db 'C:\KEYS.DAT',0
data:
