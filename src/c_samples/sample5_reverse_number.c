#include <stdio.h>

// Ví dụ 5: Đảo ngược một số
// Lỗi: Không xử lý số âm
int main() {
    int num = -123;
    int reversed = 0;
    
    // BUG: Không lưu dấu âm
    int original = num;
    if (num < 0) {
        num = -num;  // Chuyển thành dương
    }
    
    while (num > 0) {
        reversed = reversed * 10 + (num % 10);
        num /= 10;
    }
    
    if (original < 0) {
        reversed = -reversed;
    }
    
    printf("Reversed: %d\n", reversed);
    return 0;
}
